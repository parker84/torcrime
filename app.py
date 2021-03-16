import streamlit as st
import pandas as pd
import coloredlogs
import logging
import os
import time
from src.visualization.address_viz import AddressViz
from src.visualization.clustering_viz import ClusteringViz
from src.visualization.comparison_viz import CompareNeighbourhoods
from geopy.geocoders import Nominatim
import json

#----------------helpers
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)
start_time = time.process_time()
geolocator = Nominatim(user_agent="toronto_crime_app")

#-----------------setup
crime_df = pd.read_csv(
    "./data/processed/crime_data.csv").rename(columns={"long": "lon"})

#---------------sidebar filtering
app_type = st.sidebar.selectbox(
    label="Choose an Application",
    options=["Address Analysis", "Neighbourhood Comparison", "Neighbourhood Exploration"],
    index=0
)

logger.info("Sidebar filtering")
st.sidebar.markdown('### Choose Your Filters')
crime_options = st.sidebar.multiselect(
    label="Choose Crime Types",
    options=crime_df.crime_type.unique().tolist(),
    default=[
        "Assault", "Robbery"
    ]
)
location_options = st.sidebar.multiselect(
    label="Choose Location Types",
    options=crime_df.premisetype.unique().tolist(),
    default=[
        "Outside"
    ]
)
filtered_crime_df = crime_df[crime_df.crime_type.isin(
    crime_options)]
filtered_crime_df = filtered_crime_df[filtered_crime_df.premisetype.isin(
    location_options)]

if app_type == "Address Analysis":
    address_viz = AddressViz(filtered_crime_df, geolocator, crime_df.occurrenceyear.min(), crime_df.occurrenceyear.max())
    address_viz.viz_crime_counts_on_map()
    address_viz.viz_eda_plots()
    address_viz.show_dataframes()
elif app_type == "Neighbourhood Exploration":
    clust_viz = ClusteringViz(filtered_crime_df, geolocator)
    clust_viz.cluster_crimes_and_remove_outliers()
    clust_viz.set_stats_per_cluster()
    clust_viz.add_addresses_per_cluster()
    clust_viz.show_dataframes()
    clust_viz.viz_clusters()
elif app_type == "Neighbourhood Comparison":
    with open("./data/processed/Neighbourhood_Crime_Rates_Boundary_File_clean.json", "r") as f:
            counties = json.load(f)
    comp_viz = CompareNeighbourhoods(filtered_crime_df, counties)
    comp_viz.viz()

st.button("Re-run")
logger.info(f"Seconds to run: {round(time.process_time() - start_time, 2)}")