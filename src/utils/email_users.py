from tqdm import tqdm
import coloredlogs
import logging
import geopy.distance
from src.utils.emailer import Emailer
import os

class EmailUsers():

    def __init__(self, user_df):
        """Class to isolate to the right users and then send them an email

        Args:
            user_df (pd.DataFrame): user dimension dataframe, including the columns: ["lat", "lon", "km_radius", "email"]
        """
        self.user_df = user_df
        self.logger = logging.getLogger(__name__)
        self.emailer = Emailer()
        coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=self.logger)
    
    def email_the_right_users(self, sel_user_df, tweet_text, tweet_crime):
        self.logger.info("Sending emails")
        for ix, row in tqdm(sel_user_df.iterrows()):
            self.emailer.send_email(
                reciever_email=row.email,
                contents=tweet_text,
                subject=tweet_crime
            )

    def filter_to_users_near_the_event(self, tweet_lat, tweet_lon):
        user_df_event = self.user_df.copy()
        user_df_event["distance_to_address"] = self._calc_distances_to_each_user(tweet_lat, tweet_lon)
        user_df_event_filtered = user_df_event[
            user_df_event["distance_to_address"] <= user_df_event["km_radius"]
        ]
        perc_users_for_event = 100 * user_df_event_filtered.shape[0] / user_df_event.shape[0]
        self.logger.info(f"% of users for this event: {perc_users_for_event}")
        return user_df_event_filtered
    
    def _calc_distances_to_each_user(self, tweet_lat, tweet_lon):
        distances = []
        nrows = self.user_df.shape[0]
        for ix, row in tqdm(self.user_df.iterrows()):
            #     distance = geopy.distance.distance((), (row.lat, row.lon)).km # too slow, doubles the run time
            distance = geopy.distance.great_circle((tweet_lat, tweet_lon), (row.lat, row.lon)).km
            distances.append(distance)
        return distances