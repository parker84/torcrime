import ipdb # no idea why but I can't import from src without this here?
from src.utils.geocoder import GeoCoder
import tweepy
from decouple import config
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm
import datetime
import coloredlogs
from geopy.geocoders import Nominatim
import logging
import pytz
import os
import time
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)
geolocator = Nominatim(user_agent="toronto_crime_app")

class TweetScrapper():

    def __init__(self):
        auth = tweepy.OAuthHandler(config("CONSUMER_API_KEY"), config("API_SECRET_KEY"))
        auth.set_access_token(config("ACCESS_TOKEN"), config("ACCESS_TOKEN_SECRET"))
        self.api = tweepy.API(auth)
        self.engine = create_engine(f'postgresql://{config("DB_USER")}:{config("DB_PWD")}@{config("DB_HOST")}:5432/{config("DB")}')
        self.est = pytz.timezone('US/Eastern')
        self.utc = pytz.utc
        self.geocoder = GeoCoder(geolocator)

    def get_bulk_tweets_from_to_user(self, user_id, min_datetime, ops_tweet=True):
        """
        grab all the tweets from the toronto police accounts (from:TPSOperations OR from:TorontoPolice)
        since min_datetime

        Args:
            min_datetime (datetime.datetime) ex: datetime.datetime(2014, 1, 1)
        """
        tweets = []
        min_date = str(min_datetime).split(" ")[0]
        for tweet in tqdm(tweepy.Cursor(self.api.user_timeline, id=user_id, since=min_date, wait_on_rate_limit=True).items()):
            dict_tweet = tweet._json
            dict_tweet["user_name"] = dict_tweet["user"]["name"]
            if ops_tweet:
                dict_tweet = self._extract_entities_from_ops_tweet(dict_tweet)
            tweets.append(dict_tweet)
        tweet_df = pd.DataFrame(tweets)
        return tweet_df
    
    def get_tweets_from_last_n_secs(self, user_id, secs, ops_tweet=True):
        """
        grab all the tweets from the toronto police accounts (from:TPSOperations OR from:TorontoPolice)
        since min_datetime

        Args:
            min_datetime (datetime.datetime) ex: datetime.datetime(2021, 3, 27, 15, 48, 35)
        """
        min_datetime = datetime.datetime.now().astimezone(self.utc) - datetime.timedelta(seconds=secs)
        tweets = []
        min_date = str(min_datetime).split(" ")[0]
        for tweet in tweepy.Cursor(self.api.user_timeline, id=user_id, since=min_date, wait_on_rate_limit=True).items():
            dict_tweet = tweet._json
            tweet_dt = (
                datetime.datetime.strptime(dict_tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
                .replace(tzinfo=self.utc)
            )
            if tweet_dt < min_datetime:
                break
            dict_tweet["user_name"] = dict_tweet["user"]["name"]
            if ops_tweet:
                dict_tweet = self._extract_entities_from_ops_tweet(dict_tweet)
            tweets.append(dict_tweet)
        tweet_df = pd.DataFrame(tweets)
        return tweet_df
    
    def save_tweetdf_to_db(self, tweet_df, table_name, if_exists="append"):
        if tweet_df.shape[0] > 0:
            tweet_df_sel = tweet_df[[
                "id", "created_at", "text", 
                "address", "lat", "lon", "crime", "is_update", "is_crime",
                "user_name", "retweet_count", "favorite_count"
            ]]
            logger.info("tweets that occurred in the last 10 seconds:")
            logger.info(tweet_df_sel)
            tweet_df_sel.to_sql(name=table_name, con=self.engine, if_exists=if_exists, schema=config('DB_SRC_SCHEMA'))

    def _extract_entities_from_ops_tweet(self, dict_tweet):
        text = dict_tweet["text"]
        lines = text.split("\n")
        if lines[0].endswith(":") or lines[0].lower().endswith("update"):
            dict_tweet["address"] = lines[1].replace("&amp;", "and").replace("+", "and") + ", Toronto"
            dict_tweet["crime"] = lines[0].split(":")[0].lower()
            dict_tweet["is_update"] = lines[0].lower().endswith("update")
            dict_tweet["is_crime"] = True
            try:
                location = self.geocoder.geocode(dict_tweet["address"])
            except Exception as err:
                logger.error(f"Error calculating the distances: {err}, sleeping for 100s and then trying again")
                time.sleep(100)
                location = self.geocoder.geocode(dict_tweet["address"])
            if location != "Could Not Geocode Address" and location is not None:
                dict_tweet["lat"] = location.latitude
                dict_tweet["lon"] = location.longitude
            else: 
                dict_tweet["lat"] = "null"
                dict_tweet["lon"] = "null"
        else:
            dict_tweet["is_crime"] = False
            dict_tweet["address"] = "null"
            dict_tweet["crime"] = "null"
            dict_tweet["is_update"] = "null"
            dict_tweet["lat"] = "null"
            dict_tweet["lon"] = "null"
        return dict_tweet


#--------------Execution functions

def update_raw_tweet_tables(since=datetime.datetime(year=2014, month=1, day=1), if_exists="replace"):
    scrapper = TweetScrapper()
    res_df = scrapper.get_bulk_tweets_from_to_user("TPSOperations", since, ops_tweet=True)
    scrapper.save_tweetdf_to_db(res_df, "raw_tps_ops_tweets", if_exists=if_exists)
    # res_df = scrapper.get_bulk_tweets_from_to_user("TorontoPolice", since)
    # scrapper.save_tweetdf_to_db(res_df, "raw_to_police_tweets", if_exists=if_exists)
            

if __name__ == "__main__":
    update_raw_tweet_tables(since=datetime.datetime(year=2000, month=1, day=1))