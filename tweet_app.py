import os
import pathlib
import re
import plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf
import numpy as np
from geopy.geocoders import Nominatim
import logging
import coloredlogs
from decouple import config
from sqlalchemy import create_engine
import geopy.distance

#------------------Initialize 
DEFAULT_ADDRESS = "1 Dundas st East, Toronto"
CRIME_COLS = ["created_at", "crime", "address", "text"]
CRIME_MAPPINGS = {
    "fire": "Fire",
    "shooting": "Shooting",
    "stabbing": "Stabbing",
    "person with a knife": "Person with a Knife",
    "person with a gun": "Person with a Gun",
    "sound of gunshots": "Sound of Gunshots",
    "robbery": "Robbery",
    "sounds of gunshots": "Sound of Gunshots",
    "gas leak": "Gas Leak",
    "@toronto_fire fire": "Fire",
    "@torontomedics stabbing": "Stabbing",
    "@torontomedics shooting": "Shooting",
    "@toronto_fire @ttcnotices fire": "Fire",
    "@tofire fire": "Fire",
    "person w/a knife": "Person with a Knife",
}
CRIME_OPTIONS = [
    "Fire", "Shooting", "Stabbing", "Robbery", "Sound of Gunshots", "Gas Leak", "Person with a Knife", "Person with a Gun"
]
app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server
APP_PATH = str(pathlib.Path(__file__).parent.resolve())
geolocator = Nominatim(user_agent="toronto_crime_app")
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)
engine = create_engine(f'postgresql://{config("DB_USER")}:{config("DB_PWD")}@{config("DB_HOST")}:5432/{config("DB")}')

#-------------------Load data
crime_tweets = pd.read_sql(f"select * from {config('TABLE_CRIME_TWEETS')}", con=engine)
logger.info(f"Value Counts of Crimes: {crime_tweets.event.value_counts().head(40)}%") 

#----------------Clean data
crime_tweets_cleaned = crime_tweets.replace("null", np.nan).dropna(subset=["lat", "lon"], axis=0)
perc_tweets_removed = round(1 - (crime_tweets_cleaned.shape[0] / crime_tweets.shape[0]), 1)
logger.info(f"% of Rows Removed bc missing lat/lon: {perc_tweets_removed*100}%")
crime_tweets_cleaned["crime"] = crime_tweets_cleaned["event"].replace(CRIME_MAPPINGS)
crime_tweets_cleaned = crime_tweets_cleaned[crime_tweets_cleaned.crime.isin(CRIME_OPTIONS)]
crime_tweets_cleaned["created_at"] = pd.to_datetime(crime_tweets_cleaned["created_at"])
crime_tweets_cleaned = crime_tweets_cleaned.sort_values(by="created_at", ascending=False)
logger.info(f"Value Counts of Crimes: {crime_tweets_cleaned.crime.value_counts().head(40)}%")

#------------------Helpers
def calc_distances(filtered_crime_df, lat, lon):
    distances = []
    nrows = filtered_crime_df.shape[0]
    # progress_bar = st.progress(0)
    # status_text = st.empty()
    i = 1
    percentage_complete_from_last_update = 0
    for ix, row in filtered_crime_df.iterrows():
        #     distance = geopy.distance.distance((), (row.lat, row.lon)).km # too slow, doubles the run time
        distance = geopy.distance.great_circle((lat, lon), (row.lat, row.lon)).km
        distances.append(distance)
        percentage_complete = int(min(i / nrows, 1) * 100)
        # if percentage_complete != percentage_complete_from_last_update:
        #     status_text.text(f"{percentage_complete}% Complete Calculations")
        #     progress_bar.progress(percentage_complete)
        #     percentage_complete_from_last_update = percentage_complete
        i += 1
    # progress_bar.empty()
    # status_text.text("100% Complete Calculations, Now Creating Visualizations")
    return distances

def filter_crime_tweets(address, crimes, radius):
    hours = int(radius.split(" ")[0]) / 60
    km_radius = round(hours * 5, 3) # we assume 5 km/h walk speed
    location = geolocator.geocode(address)
    user_lat, user_lon = location.latitude, location.longitude
    crime_tweets_cleaned["distance_to_address"] = calc_distances(crime_tweets_cleaned, user_lat, user_lon)
    crime_tweets_filtered = (
        crime_tweets_cleaned
        [crime_tweets_cleaned["crime"].isin(crimes)]
        [crime_tweets_cleaned["distance_to_address"] <= km_radius]
    )
    return crime_tweets_filtered


#-------------Setting up default filters
crime_tweets_filtered = filter_crime_tweets(DEFAULT_ADDRESS, ["suspicious package", "stabbing"], "5 minutes")




#----------------App layout

app.layout = html.Div(
    id="root",
    children=[
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(
                                            "Recent Crimes",
                                            style={"margin-bottom": "0px"},
                                        ),
                                        html.H5(
                                            "Recent Tweets", style={"margin-top": "0px"}
                                        ),
                                    ]
                                )
                            ],
                            className="one-half column",
                            id="title",
                        ),
                ],
                id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="address-container",
                            children=[
                                html.P(
                                    id="address-text",
                                    children="Enter the address of interest",
                                ),
                                dcc.Input(
                                    id="address-input",
                                    type="text",
                                    placeholder=DEFAULT_ADDRESS,
                                    debounce=True
                                )
                            ],
                        ),
                        html.Div(
                            id="crime-checklist-container",
                            children=[
                                html.P(
                                    id="crime-checks-text",
                                    children="Choose your crime types of interest:",
                                ),
                                dcc.Checklist(
                                    id="crime-checker",
                                    options=[
                                        {'label': crime, 'value': crime}
                                        for crime in CRIME_OPTIONS
                                    ],
                                    value=CRIME_OPTIONS
                                ), 
                            ],
                        ),
                        html.Div(
                            id="walking-radius-container",
                            children=[
                                html.P(
                                    id="radius-text",
                                    children="Select Walking Distance Radius (Based on the average walking speed of 5km/h)",
                                ),
                                dcc.Dropdown(
                                    id="radius-dropdown",
                                    options=[
                                        {'label': t, 'value': t}
                                        for t in ["1 minute", "5 minutes", "10 minutes", "15 minutes", "30 minutes"]
                                    ],
                                    value="5 minutes"
                                ), 
                            ],
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H5(
                                            "Recent crime within your radius:"
                                        ),
                                    ]
                                )
                            ],
                            id="heatmap-title-intro",
                        ),
                        html.Div(
                            id="tweets-container",
                            children=[
                                html.P(
                                   f"Tweets of crime in your area",
                                    id="tweets-title",
                                ),
                                dash_table.DataTable(
                                    id='tweets',
                                    columns=[{"name": i, "id": i} for i in CRIME_COLS]
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)



#-------------callbacks
@app.callback(
    Output("tweets", "data"),
    [
        Input("address-input", "value"), 
        Input("crime-checker", "value"),
        Input("radius-dropdown", "value"),
    ],
)
def display_tweets(address, crimes, radius):
    if address is None:
        address = DEFAULT_ADDRESS
    logger.info("Filtering tweets")
    crime_tweets_filtered = filter_crime_tweets(address, crimes, radius)[CRIME_COLS]
    logger.info("Tweets filtered, showing table")
    logger.info(f"{crime_tweets_filtered.describe().T}")
    return crime_tweets_filtered.to_dict('records')

if __name__ == "__main__":
    # app.run_server(debug=True, port=8053)
    app.run_server()
