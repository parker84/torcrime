import tweepy
from decouple import config
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from tqdm import tqdm
import datetime
import coloredlogs
import logging
import pytz
import os
import time
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)

class TweetScrapper():

    def __init__(self):
        auth = tweepy.OAuthHandler(config("CONSUMER_API_KEY"), config("API_SECRET_KEY"))
        auth.set_access_token(config("ACCESS_TOKEN"), config("ACCESS_TOKEN_SECRET"))
        self.api = tweepy.API(auth)
        self.engine = create_engine(f'postgresql://{config("DB_USER")}:{config("DB_PWD")}@{config("DB_HOST")}:5432/{config("DB")}')
        self.est = pytz.timezone('US/Eastern')
        self.utc = pytz.utc

    def get_bulk_tweets_from_to_user(self, user_id, min_datetime):
        """
        grab all the tweets from the toronto police accounts (from:TPSOperations OR from:TorontoPolice)
        since min_datetime

        Args:
            min_datetime (datetime.datetime) ex: datetime.datetime(2021, 3, 27, 15, 48, 35)
        """
        tweets = []
        min_date = str(min_datetime).split(" ")[0]
        for tweet in tqdm(tweepy.Cursor(self.api.user_timeline, id=user_id, since=min_date).items()):
            dict_tweet = tweet._json
            dict_tweet["user_name"] = dict_tweet["user"]["name"]
            tweets.append(dict_tweet)
        tweet_df = pd.DataFrame(tweets)
        return tweet_df
    
    def get_recent_tweets_from_to_user(self, user_id, min_datetime):
        """
        grab all the tweets from the toronto police accounts (from:TPSOperations OR from:TorontoPolice)
        since min_datetime

        Args:
            min_datetime (datetime.datetime) ex: datetime.datetime(2021, 3, 27, 15, 48, 35)
        """
        tweets = []
        min_date = str(min_datetime).split(" ")[0]
        for tweet in tweepy.Cursor(self.api.user_timeline, id=user_id, since=min_date).items():
            dict_tweet = tweet._json
            tweet_dt = (
                datetime.datetime.strptime(dict_tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
                .replace(tzinfo=self.utc)
            )
            if tweet_dt < min_datetime:
                break
            dict_tweet["user_name"] = dict_tweet["user"]["name"]
            tweets.append(dict_tweet)
        tweet_df = pd.DataFrame(tweets)
        return tweet_df
    
    def save_tweetdf_to_db(self, tweet_df, table_name, if_exists="append"):
        if tweet_df.shape[0] > 0:
            tweet_df_sel = tweet_df[[
                "id", "created_at", "text", "retweet_count", "favorite_count", "user_name"
            ]]
            logger.info("tweets that occurred in the last 10 seconds:")
            logger.info(tweet_df_sel)
            tweet_df_sel.to_sql(name=table_name, con=self.engine, if_exists=if_exists)
    
    def get_tweets_from_last_n_secs(self, user_id, secs=10):
        dt_n_secs_ago = datetime.datetime.now().astimezone(self.utc) - datetime.timedelta(seconds=secs)
        return self.get_recent_tweets_from_to_user(user_id, dt_n_secs_ago)

def replace_raw_tweet_tables(since=datetime.datetime(year=2014, month=1, day=1)):
    scrapper = TweetScrapper()
    res_df = scrapper.get_bulk_tweets_from_to_user("TorontoPolice", since)
    scrapper.save_tweetdf_to_db(res_df, "raw_to_police_tweets", if_exists="replace")
    res_df = scrapper.get_bulk_tweets_from_to_user("TPSOperations", since)
    scrapper.save_tweetdf_to_db(res_df, "raw_tps_ops_tweets", if_exists="replace")

def append_to_streaming_raw_tweet_tables_every_n_secs(secs=10, log_every=1000):
    logger.info('Starting to listen')
    logger.info(f'Making requests every {secs}s, logging every {log_every}s')
    scrapper = TweetScrapper()
    i = 0
    while True != False:
        if i % log_every == 0:
            logger.info(f'Making request number: {i+1}')
        res_df = scrapper.get_tweets_from_last_n_secs("TorontoPolice", secs)
        scrapper.save_tweetdf_to_db(res_df, "streaming_raw_to_police_tweets", if_exists="append")
        res_df = scrapper.get_tweets_from_last_n_secs("TPSOperations", secs)
        scrapper.save_tweetdf_to_db(res_df, "streaming_raw_tps_ops_tweets", if_exists="append")
        i += 1
        time.sleep(secs)
            

if __name__ == "__main__":
    replace_raw_tweet_tables(since=datetime.datetime(year=2014, month=1, day=1))
    append_to_streaming_raw_tweet_tables_every_n_secs(secs=10, log_every=10000)
