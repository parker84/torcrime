import streamlit as st
import pandas as pd
import coloredlogs
import logging
import os
import time
from PIL import Image

from src.visualization.address_viz import AddressViz
# from src.visualization.clustering_viz import ClusteringViz
from src.visualization.comparison_viz import CompareNeighbourhoods
import json
import streamlit_analytics
cn_tower_image = Image.open('./assets/FlaviConTC.png')
st.set_page_config(layout='wide', page_icon=cn_tower_image, page_title='TorCrime Dashboard')

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
CITY_REGIONS = [
    'Toronto', 'East York', 'Old Toronto', 'Etobicoke', 'North York', 'Scarborough', 'York'
]

@st.cache
def load_crime_data():
    crime_df = pd.read_csv("./data/processed/crime_data.csv").rename(columns={"long": "lon"})
    crime_df['crime_type'] = crime_df['crime_type'].replace('Theft Over', 'Theft Over $5k')
    crime_types = crime_df.crime_type.unique().tolist()
    crime_locations = crime_df.premisetype.unique().tolist()
    return crime_df, crime_types, crime_locations

#-----------------setup
crime_df, crime_types, crime_locations = load_crime_data()
st.title("📊 Toronto Crime Data")
st.sidebar.title('TorCrime')
st.sidebar.image(cn_tower_image, width=100)

address = st.text_input(
    "Enter your address", 
    value="1 Dundas St, Toronto",
    help="Format: <street #> <street name>, Toronto"
)
walking_mins_str = st.sidebar.selectbox(
    label="Select Walking Distance Radius",
    options=["1 minute", "5 minutes", "10 minutes", "15 minutes", "30 minutes"],
    index=2,
    help="Based on the average walking speed of 5km/h"
)

st.markdown(
    f'View crimes that have occurred between {int(crime_df.occurrenceyear.min())}-{int(crime_df.occurrenceyear.max())}, and view analytical reports for this address.'
)
crime_options = st.sidebar.multiselect(
    label="Choose Crime(s)",
    options=crime_types,
    default=[
        "Assault", "Robbery"
    ]
)
location_options = st.sidebar.multiselect(
    label="Choose Location(s)",
    options=crime_locations,
    default=[
        "Outside"
    ]
)
filtered_crime_df = crime_df[crime_df.crime_type.isin(
    crime_options)]
filtered_crime_df = filtered_crime_df[filtered_crime_df.premisetype.isin(
    location_options)]

with st.expander('Address Crime Report', expanded=True):
    st.markdown("### Address Crime Report")
    st.markdown(f"This report will enable the user to view historical crime trends.")
    if st.button('Create Address Crime Report'):
        address_viz = AddressViz(
            address, walking_mins_str, filtered_crime_df, crime_df.occurrenceyear.min(), 
            crime_df.occurrenceyear.max(), INITIAL_RANDOM_ADDRESSES
        )
        address_viz.viz_close_neighbourhood_rankings()
        address_viz.viz_eda_plots()
        address_viz.viz_crime_counts_on_map()
        address_viz.show_dataframes()

st.markdown("#### Neighbourhood Crime Report")
st.markdown("This report will enable the user to compare crime rates between different neighbourhoods")
with open("./data/processed/Neighbourhood_Crime_Rates_Boundary_File_clean.json", "r") as f:
    counties = json.load(f)
comp_viz = CompareNeighbourhoods(filtered_crime_df, counties)
submitted = comp_viz.create_filter_form()

if submitted:
    comp_viz.filter_df_by_time()
    comp_viz.viz()
# with st.expander('Crime Cluster Report', expanded=False):
#     st.markdown("#### Crime Cluster Report")
#     st.markdown("This report will enable the user to understand where the crime clusters are within each neighbourhood of interest.")
#     clust_viz = ClusteringViz(filtered_crime_df)
#     submitted = clust_viz.create_filter_form()
#     if submitted:
#         clust_viz.filter_to_neighbourhoods()
#         clust_viz.cluster_crimes_and_remove_outliers()
#         clust_viz.set_stats_per_cluster()
#         clust_viz.add_addresses_per_cluster()
#         clust_viz.viz_clusters()
#         clust_viz.show_dataframes()


logger.info(f"Seconds to run: {round(time.process_time() - start_time, 2)}")
streamlit_analytics.stop_tracking()