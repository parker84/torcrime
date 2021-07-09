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

#------------------Initialize 
CRIME_COLS = ["Date of Report", "Crime", "Address", "Time of Report", "Full Text"]
ALERTING_CRIME_OPTIONS = [
    "Fire", "Shooting", "Stabbing", "Robbery", "Sound of Gunshots", "Gas Leak", "Person with a Knife", 
    "Person with a Gun", "Missing", "Protest", "Industrial Accident", "Wires Down", "Marine Rescue",
    "Collision", "Police Investigation", "Demonstration", "Assault"
]
CRIME_REGEX = {
    "fire": "Fire",
    "shooting": "Shooting",
    "stabbing": "Stabbing",
    "robbery": "Robbery",
    "gunshot": "Sound of Gunshots",
    "gas leak": "Gas Leak",
    "knife": "Person With a Knife",
    "gun\s": "Person with a Gun",
    "gun$": "Person with a Gun",
    "missing": "Missing",
    "protest": "Protest",
    "industrial accident": "Industrial Accident",
    "wires down": "Wires Down",
    "marine rescue": "Marine Rescue",
    "collision": "Collision",
    "police investigation": "Police Investigation",
    "demonstration": "Demonstration",
    "assault": "Assault"
}
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)
engine = create_engine(f'postgresql://{config("DB_USER")}:{config("DB_PWD")}@{config("DB_HOST")}:5432/{config("DB")}')

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
    status_text.text("100% Complete Calculations, Now Creating Visualizations")
    return distances

#-------------AddressViz
class TweetViz():
    
    def __init__(self, alert_crime_options, initial_random_addresses, geolocator, filtered_crime_df=crime_tweets_cleaned):
        self.filtered_crime_df = filtered_crime_df[filtered_crime_df.crime.isin(alert_crime_options)]
        self.geocoder = GeoCoder(geolocator)
        self.initial_random_addresses = initial_random_addresses
        self.show_intro_text()
        self.filter_crime_df_within_radius()

    def show_intro_text(self):
        st.markdown("#### This platform will provide details about recent alerts around a specific address of interest")

    def filter_crime_df_within_radius(self):
        logger.info("Filtering to radius around address")
        self.address = st.text_input(
            "Enter the address and district of interest (format: [street #] [street name], Toronto)", 
            value="Enter Address Here (format: [street #] [street name], Toronto)",
            help="Format: <street #> <street name>, Toronto (Or one of the 6 districts: Old Toronto, East York, Etobicoke, North York, Scarborough, York)"
        )
        if self.address == "Enter Address Here (format: [street #] [street name], Toronto)":
            self.address = np.random.choice(self.initial_random_addresses)
        self.walking_mins_str = st.selectbox(
            label="Select Walking Distance Radius (Based on the average walking speed of 5km/h)",
            options=["1 minute", "5 minutes", "10 minutes", "15 minutes", "30 minutes", "60 minutes"],
            index=4
        )
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
    
    def viz(self):
        st.markdown(f"## Recent Crime Alerts")
        st.markdown(f"For {self.address}")
        crime_counts = pd.DataFrame(
            self.filtered_crime_df_within_radius.drop_duplicates(subset=["Crime", "Address", "Date of Report"])
            ["Crime"].value_counts().reset_index()
            .rename(columns={
                "Crime": "Number of Alerts",
                "index": "Crime"
            })
        )
        bars = alt.Chart(crime_counts).mark_bar().encode(
            x='Number of Alerts',
            y="Crime"
        )
        st.altair_chart(bars, use_container_width=True)
        st.markdown("Get real-time email alerts for this address: [**Sign Up Now**](http://torcrime.com/products/crime-alerts)")
        st.dataframe(
            self.filtered_crime_df_within_radius[["Crime", "Address", "Full Text", "Date of Report", "Time of Report"]], 
            height=500
        )
        st.text("Hover for details")
