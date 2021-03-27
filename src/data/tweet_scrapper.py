import tweepy
from decouple import config
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
engine = create_engine('postgresql://username:password@localhost:5432/mydatabase')
df.to_sql('table_name', engine)

class TweetScrapper():

    def __init__(self):
        auth = tweepy.OAuthHandler(config("CONSUMER_API_KEY"), config("API_SECRET_KEY"))
        auth.set_access_token(config("ACCESS_TOKEN"), config("ACCESS_TOKEN_SECRET"))
        self.api = tweepy.API(auth)
        self.engine = create_engine(f'postgresql://{config("DB_USER")}:{config("DB_PWD")}@{config("DB_HOST")}:5432/{config("DB")}')

    def get_tweets_from_to_police(self, user_id, min_date):
        """
        grab all the tweets from the toronto police accounts (from:TPSOperations OR from:TorontoPolice)
        since min_date

        Args:
            min_date (str) ex:2014-07-19
        
        Examples:
        >>> scrapper = TweetScrapper()
        >>> res_df = scrapper.get_tweets_from_to_police("TPSOperations", "2021-03-20")
        """
        tweets = []
        for tweet in tweepy.Cursor(self.api.user_timeline, id=user_id, since=min_date).items():
            tweets.append(tweet._json)
        tweet_df = pd.DataFrame(tweets)
        return tweet_df
    
    def save_tweetdf_to_db(self, tweet_df, table_name, if_exists="append"):
        tweet_df[[
            "id", "created_at", "text", "retweet_count", "favorite_count", "user"
        ]].to_sql(name=table_name, con=self.engine, if_exists=if_exists)

if __name__ == "__main__":
    scrapper = TweetScrapper()
    res_df = scrapper.get_tweets_from_to_police("TorontoPolice", "2021-03-20")
    scrapper.save_tweetdf_to_db(res_df, "raw_to_police_tweets")
    res_df = scrapper.get_tweets_from_to_police("TPSOperations", "2021-03-20")
    scrapper.save_tweetdf_to_db(res_df, "raw_tps_ops_tweets")