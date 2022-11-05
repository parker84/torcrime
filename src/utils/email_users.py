from tqdm import tqdm
import coloredlogs
import logging
import geopy.distance
from src.utils.emailer import Emailer
import os
import pandas as pd

#--------------logging setup
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"))
fh = logging.FileHandler('logs/alert_app.log')
logger.addHandler(fh)
fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))


class EmailUsers():

    def __init__(self, user_df):
        """Class to isolate to the right users and then send them an email

        Args:
            user_df (pd.DataFrame): user dimension dataframe, including the columns: ["lat", "lon", "km_radius", "email"]
        """
        self.user_df = user_df
        self.emailer = Emailer()
    
    def email_the_right_users(self, sel_user_df, tweet):
        """[summary]

        Args:
            sel_user_df (pandas dataframe): isolated to users within radius, and having the columns: ["email"]
            tweet (row of a pandas dataframe): with the following columns: ["text", "crime", "address", "created_at"]
        """
        logger.info("Sending emails")
        subject = f"TorCrime | {tweet.crime} @ {tweet.address}"
        tweet["created_at_est"] = pd.to_datetime(tweet["created_at"]).tz_convert("EST")
        for ix, row in tqdm(sel_user_df.iterrows()):
            contents = [
                f"Hi 👋🏻,\n",
                "There has been a crime reported near your address.\n\n",
                f"Crime: {tweet.crime}\n",
                f"Location of Crime: {tweet.address}\n",
                f"Time of Crime: {str(tweet.created_at_est.time())}\n",
                f"Date of Crime: {str(tweet.created_at_est.date())}\n\n",
                f"See full details below:\n",
                f"{tweet.text}\n\n",
                "Thank you for using our service and please let us know if there's anything we can do to improve it for you.\n\n",
                "Best,\n",
                "Brydon\n",
            ]
            self.emailer.send_email(
                reciever_email=row.email,
                contents=contents,
                subject=subject
            )

    def filter_to_users_near_the_event(self, tweet_lat, tweet_lon):
        user_df_event = self.user_df.copy()
        try:
            tweet_lat, tweet_lon = float(tweet_lat), float(tweet_lon)
            user_df_event["distance_to_address"] = self._calc_distances_to_each_user(tweet_lat, tweet_lon)
            user_df_event_filtered = user_df_event[
                user_df_event["distance_to_address"] <= user_df_event["km_radius"]
            ]
            perc_users_for_event = 100 * user_df_event_filtered.shape[0] / user_df_event.shape[0]
            logger.info(f"% of users for this event: {perc_users_for_event}")
            return user_df_event_filtered
        except ValueError:
            return user_df_event.iloc[0:0]
        
    
    def _calc_distances_to_each_user(self, tweet_lat, tweet_lon):
        distances = []
        nrows = self.user_df.shape[0]
        for ix, row in tqdm(self.user_df.iterrows()):
            #     distance = geopy.distance.distance((), (row.lat, row.lon)).km # too slow, doubles the run time
            distance = geopy.distance.great_circle((tweet_lat, tweet_lon), (row.lat, row.lon)).km
            distances.append(distance)
        return distances