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
st.set_page_config(layout='wide')

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
    crime_types = crime_df.crime_type.unique().tolist()
    crime_locations = crime_df.premisetype.unique().tolist()
    return crime_df, crime_types, crime_locations

#-----------------setup
crime_df, crime_types, crime_locations = load_crime_data()
st.title("Toronto Crime Dashboard")
st.markdown(
    """This dashboard enables the user to:
    
    1. Identify crimes occuring near an address
    2. Identify crime trends near an address (year over year, and peak times during the week)
    3. Compare crime rates between different neighbourhoods
    4. Identify crime clusters within one or more neighbourhoods
    """
)
st.markdown("**To Begin:** Enter an address in the sidebar of this dashboard (press the arrow in the top left on mobile).")
st.sidebar.title('TorCrime')
image = Image.open('./assets/FlaviConTC.png')
st.sidebar.image(image, width=100)

#---------------sidebar
street_name_and_number = st.sidebar.text_input(
    "Enter the address of interest", 
    value='Enter Address Here (ex: "1 Dundas St")',
    help="Format: <street #> <street name>"
)
city = st.sidebar.selectbox(
    label="Select the city/region of address",
    options=CITY_REGIONS,
    index=0,
    help='Selecting the specific region or just selecting Toronto should work.'
)
address = f'{street_name_and_number}, {city}'
walking_mins_str = st.sidebar.selectbox(
    label="Select Walking Distance Radius",
    options=["1 minute", "5 minutes", "10 minutes", "15 minutes", "30 minutes"],
    index=1,
    help="Based on the average walking speed of 5km/h"
)
st.sidebar.markdown('### Get Real-Time Email Alerts About Crimes Occuring Near You')
st.sidebar.markdown("**[Sign Up Now](http://torcrime.com/products/crime-alerts)**")
st.sidebar.markdown('Please let us know how we can make [TorCrime](https://torcrime.com) better for you: [Contact Us](https://torcrime.com/pages/contact-us)')

#------------dash
st.markdown('## Recent Crimes')
st.markdown(f'View crimes that have occurred recently within `{walking_mins_str}` radius around the chosen address and see details around each crime.')
alert_crime_options = st.multiselect(
    label="Choose Crime(s)",
    options=ALERTING_CRIME_OPTIONS,
    default=ALERTING_CRIME_DEFAULTS
)
tweet_viz = TweetViz(address, walking_mins_str, alert_crime_options, INITIAL_RANDOM_ADDRESSES)
tweet_viz.viz()

st.markdown('## Historical Crimes')
st.markdown(
    f'View crimes that have occurred between {int(crime_df.occurrenceyear.min())}-{int(crime_df.occurrenceyear.max())}, and view analytical reports for this address.'
)
crime_options = st.multiselect(
    label="Choose Crime(s)",
    options=crime_types,
    default=[
        "Assault", "Robbery"
    ]
)
location_options = st.multiselect(
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
with st.expander('Neighbourhood Crime Report', expanded=False):
    st.markdown("#### Neighbourhood Crime Report")
    st.markdown("This report will enable the user to compare crime rates between different neighbourhoods")
    with open("./data/processed/Neighbourhood_Crime_Rates_Boundary_File_clean.json", "r") as f:
        counties = json.load(f)
    comp_viz = CompareNeighbourhoods(filtered_crime_df, counties)
    submitted = comp_viz.create_filter_form()
    if submitted:
        comp_viz.filter_df_by_time()
        comp_viz.viz()
with st.expander('Crime Cluster Report', expanded=False):
    st.markdown("#### Crime Cluster Report")
    st.markdown("This report will enable the user to understand where the crime clusters are within each neighbourhood of interest.")
    clust_viz = ClusteringViz(filtered_crime_df)
    submitted = clust_viz.create_filter_form()
    if submitted:
        clust_viz.filter_to_neighbourhoods()
        clust_viz.cluster_crimes_and_remove_outliers()
        clust_viz.set_stats_per_cluster()
        clust_viz.add_addresses_per_cluster()
        clust_viz.viz_clusters()
        clust_viz.show_dataframes()

st.markdown("Thanks for checking out our Dashboard!")
st.markdown("Consider supporting us by getting real-time email alerts for your address: [**Sign Up Now**](http://torcrime.com/products/crime-alerts)")
st.button("Re-run")
logger.info(f"Seconds to run: {round(time.process_time() - start_time, 2)}")
streamlit_analytics.stop_tracking()