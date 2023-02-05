import os
import pandas as pd
import pandas as pd
import numpy as np
from src.utils.geocoder import GeoCoder
import logging
import coloredlogs
from decouple import config
from sqlalchemy import create_engine
import geopy.distance
import streamlit as st
import altair as alt
import time
from src.constants import (
    CRIME_COLS,
    ALERTING_CRIME_OPTIONS,
    CRIME_REGEX
)

#------------------Initialize 
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)
engine = create_engine(config('DATABASE_URL'))

#-------------------Load data
crime_tweets = pd.read_sql(
    f"select * from {config('DB_SRC_SCHEMA')}.{config('TABLE_CRIME_TWEETS')}", 
    con=engine
)
logger.info(f"Value Counts of Crimes: {crime_tweets.crime.value_counts().head(40)}%")

#----------------Clean data
crime_tweets_cleaned = crime_tweets.replace("null", np.nan).dropna(subset=["lat", "lon"], axis=0)
perc_tweets_removed = round(1 - (crime_tweets_cleaned.shape[0] / crime_tweets.shape[0]), 1)
logger.info(f"% of Rows Removed bc missing lat/lon: {perc_tweets_removed*100}%")
crime_tweets_cleaned["crime"] = crime_tweets_cleaned["crime"].str.lower()
for regex in CRIME_REGEX:
    crime_tweets_cleaned["crime"] = crime_tweets_cleaned["crime"].str.replace(f".*{regex}.*", CRIME_REGEX[regex], regex=True)
crime_tweets_cleaned = crime_tweets_cleaned[crime_tweets_cleaned.crime.isin(ALERTING_CRIME_OPTIONS)]
crime_tweets_cleaned["created_at"] = pd.to_datetime(crime_tweets_cleaned["created_at"])
crime_tweets_cleaned["created_at_est"] = crime_tweets_cleaned["created_at"].dt.tz_convert("EST")
crime_tweets_cleaned["Date of Report"] = crime_tweets_cleaned["created_at_est"].dt.date
crime_tweets_cleaned["Time of Report"] = crime_tweets_cleaned["created_at_est"].dt.time
crime_tweets_cleaned = crime_tweets_cleaned.sort_values(by="created_at_est", ascending=False)
logger.info(f"Value Counts of Crimes: {crime_tweets_cleaned.crime.value_counts().head(40)}%")

#------------------Helpers
def calc_distances(filtered_crime_df, lat, lon):
    distances = []
    nrows = filtered_crime_df.shape[0]
    progress_bar = st.progress(0)
    status_text = st.empty()
    i = 1
    percentage_complete_from_last_update = 0
    for ix, row in filtered_crime_df.iterrows():
        #     distance = geopy.distance.distance((), (row.lat, row.lon)).km # too slow, doubles the run time
        distance = geopy.distance.great_circle((lat, lon), (row.lat, row.lon)).km
        distances.append(distance)
        percentage_complete = int(min(i / nrows, 1) * 100)
        if percentage_complete != percentage_complete_from_last_update:
            status_text.text(f"{percentage_complete}% Complete Calculations")
            progress_bar.progress(percentage_complete)
            percentage_complete_from_last_update = percentage_complete
        i += 1
    progress_bar.empty()
    return distances

#-------------AddressViz
class TweetViz():
    
    def __init__(self, address, walking_mins_str, alert_crime_options, initial_random_addresses, filtered_crime_df=crime_tweets_cleaned):
        self.address = address
        self.walking_mins_str = walking_mins_str
        self.filtered_crime_df = filtered_crime_df[filtered_crime_df.crime.isin(alert_crime_options)]
        self.geocoder = GeoCoder()
        self.initial_random_addresses = initial_random_addresses
        self.filter_crime_df_within_radius()

    def filter_crime_df_within_radius(self):
        logger.info("Filtering to radius around address")
        if self.address == 'Enter Address Here (ex: "1 Dundas St"), Toronto':
            self.address = np.random.choice(self.initial_random_addresses)
        hours = int(self.walking_mins_str.split(" ")[0]) / 60
        km_radius = round(hours * 5, 3) # we assume 5 km/h walk speed
        try:
            location = self.geocoder.geocode(self.address)
        except Exception as err:
            logger.warn(f"{err}")
            logger.warn(f"sleeping for 5 secs and trying again")
            time.sleep(5)
            location = self.geocoder.geocode(self.address)
        self.lat, self.lon = location.latitude, location.longitude
        self.filtered_crime_df["distance_to_address"] = calc_distances(self.filtered_crime_df, self.lat, self.lon)
        filtered_crime_df_within_radius = (
            self.filtered_crime_df
            [self.filtered_crime_df["distance_to_address"] <= km_radius]
        )
        n_crimes = filtered_crime_df_within_radius.shape[0]
        self.filtered_crime_df_within_radius = filtered_crime_df_within_radius.rename(
            columns={
                "crime": "Crime", 
                "address": "Address", 
                "text": "Full Text"
            }
        )[CRIME_COLS]
        logger.info("Filtered to radius around address")
    
    def viz(self, show_chart=False):
        crime_counts = pd.DataFrame(
            self.filtered_crime_df_within_radius.drop_duplicates(subset=["Crime", "Address", "Date of Report"])
            ["Crime"].value_counts().reset_index()
            .rename(columns={
                "Crime": "Number of Alerts",
                "index": "Crime"
            })
        )
        if show_chart:
            bars = alt.Chart(crime_counts).mark_bar().encode(
                x='Number of Alerts',
                y="Crime"
            )
            st.altair_chart(bars, use_container_width=True)
        viz_df = self.filtered_crime_df_within_radius[
            ["Crime", "Address", "Full Text", "Date of Report", "Time of Report"]
        ]
        viz_df["Time of Report"] = viz_df["Time of Report"].astype(str)
        st.dataframe(viz_df)