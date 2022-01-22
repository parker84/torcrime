import streamlit as st
import pandas as pd
import coloredlogs
import logging
import os
import time
from PIL import Image

from src.visualization.address_viz import AddressViz
from src.visualization.clustering_viz import ClusteringViz
from src.visualization.comparison_viz import CompareNeighbourhoods
from src.visualization.tweet_viz import TweetViz, ALERTING_CRIME_OPTIONS, ALERTING_CRIME_DEFAULTS
import json
import streamlit_analytics

#----------------helpers
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)
start_time = time.process_time()
streamlit_analytics.start_tracking()
INITIAL_RANDOM_ADDRESSES = [
    "1 Dundas st East, Toronto", 
    "584 King st West, Toronto", 
    "Sherbourne Street and Dundas Street East, Toronto", 
    "147 Gerrard Street East, Toronto",
    "505 Church Street, Toronto",
    "42 Widmer Street, Toronto",
    "391 Yonge Street, Toronto",
    "12 Glen Baillie Place, Toronto",
    "237 Queen Street East, Toronto",
    "467 Yonge Street, Toronto"
]

@st.cache
def load_crime_data():
    crime_df = pd.read_csv("./data/processed/crime_data.csv").rename(columns={"long": "lon"})
    crime_types = crime_df.crime_type.unique().tolist()
    crime_locations = crime_df.premisetype.unique().tolist()
    return crime_df, crime_types, crime_locations

#-----------------setup
crime_df, crime_types, crime_locations = load_crime_data()
st.title("Toronto Crime Dashboard")
st.sidebar.title('TorCrime')
image = Image.open('./assets/FlaviConTC.png')
st.sidebar.image(image, width=100)

#---------------sidebar
address = st.sidebar.text_input(
    "Enter the address and district of interest (format: [street #] [street name], Toronto)", 
    value="Enter Address Here (format: [street #] [street name], Toronto)",
    help="Format: <street #> <street name>, Toronto (Or one of the 6 districts: Old Toronto, East York, Etobicoke, North York, Scarborough, York)"
)
walking_mins_str = st.sidebar.selectbox(
    label="Select Walking Distance Radius",
    options=["1 minute", "5 minutes", "10 minutes", "15 minutes", "30 minutes"],
    index=1,
    help="Based on the average walking speed of 5km/h"
)

#------------dash
st.markdown('### Recent Crimes')
alert_crime_options = st.multiselect(
    label="Choose Crime Types",
    options=ALERTING_CRIME_OPTIONS,
    default=ALERTING_CRIME_DEFAULTS
)
tweet_viz = TweetViz(address, walking_mins_str, alert_crime_options, INITIAL_RANDOM_ADDRESSES)
tweet_viz.viz()

st.markdown('### Historical Crimes')
crime_options = st.multiselect(
    label="Choose Crime Types",
    options=crime_types,
    default=[
        "Assault", "Robbery"
    ]
)
location_options = st.multiselect(
    label="Choose Location Types",
    options=crime_locations,
    default=[
        "Outside"
    ]
)
filtered_crime_df = crime_df[crime_df.crime_type.isin(
    crime_options)]
filtered_crime_df = filtered_crime_df[filtered_crime_df.premisetype.isin(
    location_options)]

with st.expander('Address Crime Analysis', expanded=False):
    address_viz = AddressViz(
        address, walking_mins_str, filtered_crime_df, crime_df.occurrenceyear.min(), 
        crime_df.occurrenceyear.max(), INITIAL_RANDOM_ADDRESSES
    )
    address_viz.viz_close_neighbourhood_rankings()
    address_viz.viz_eda_plots()
    address_viz.viz_crime_counts_on_map()
    address_viz.show_dataframes()
with st.expander('Neighbourhood Crime Comparison', expanded=False):
    with open("./data/processed/Neighbourhood_Crime_Rates_Boundary_File_clean.json", "r") as f:
            counties = json.load(f)
    comp_viz = CompareNeighbourhoods(filtered_crime_df, counties)
    comp_viz.viz()
with st.expander('Toronto Crime Clusters', expanded=False):
    clust_viz = ClusteringViz(filtered_crime_df)
    clust_viz.cluster_crimes_and_remove_outliers()
    clust_viz.set_stats_per_cluster()
    clust_viz.add_addresses_per_cluster()
    clust_viz.viz_clusters()
    clust_viz.show_dataframes()


st.sidebar.markdown('### Get Real-Time Email Alerts About Crimes Occuring Near You')
st.sidebar.markdown("**[Sign Up Now](http://torcrime.com/products/crime-alerts)**")
st.sidebar.markdown('Please let us know how we can make [TorCrime](https://torcrime.com) better for you: [Contact Us](https://torcrime.com/pages/contact-us)')

st.markdown("Thanks for checking out our Dashboard!")
st.markdown("Consider supporting us by getting real-time email alerts for your address: [**Sign Up Now**](http://torcrime.com/products/crime-alerts)")
st.button("Re-run")
logger.info(f"Seconds to run: {round(time.process_time() - start_time, 2)}")
streamlit_analytics.stop_tracking()