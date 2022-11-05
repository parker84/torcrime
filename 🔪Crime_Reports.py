import streamlit as st
import pandas as pd
import coloredlogs
import logging
import os
import time
from PIL import Image

from src.visualization.tweet_viz import TweetViz, ALERTING_CRIME_OPTIONS, ALERTING_CRIME_DEFAULTS
from src.utils.users import Users
import streamlit_analytics
cn_tower_image = Image.open('./assets/FlaviConTC.png')
st.set_page_config(layout='wide', page_icon=cn_tower_image, page_title='TorCrime Dashboard')
users = Users()

#----------------helpers
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)
start_time = time.process_time()
streamlit_analytics.start_tracking()


@st.cache
def load_crime_data():
    crime_df = pd.read_csv("./data/processed/crime_data.csv").rename(columns={"long": "lon"})
    crime_df['crime_type'] = crime_df['crime_type'].replace('Theft Over', 'Theft Over $5k')
    crime_types = crime_df.crime_type.unique().tolist()
    crime_locations = crime_df.premisetype.unique().tolist()
    return crime_df, crime_types, crime_locations

#-----------------setup
crime_df, crime_types, crime_locations = load_crime_data()
st.title("🔪 Toronto Crime Reports")
st.sidebar.title('TorCrime')
st.sidebar.image(cn_tower_image, width=100)

#---------------sidebar
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
alert_crime_options = st.sidebar.multiselect(
    label="Choose Crime(s)",
    options=ALERTING_CRIME_OPTIONS,
    default=ALERTING_CRIME_DEFAULTS
)
st.sidebar.markdown('Please let us know how we can make TorCrime better for you: [Contact Us](https://torcrime.com/pages/contact-us)')

#------------dash
tweet_viz = TweetViz(address, walking_mins_str, alert_crime_options, "1 Dundas st East, Toronto")
tweet_viz.viz()

#-----------email
st.markdown('### Crime Alerts')
email = st.text_input('Enter Your Email to Receive Crime Alerts For This Address', 'your_email@gmail.com')
if email != 'your_email@gmail.com':
    users.create_user(email, address)
    st.markdown(f"Success! Alerts will be sent to `{email}` about address: `{address}`")

st.markdown('### Crime Data')
st.markdown('See more Crime Data for your address here: **[📊 Crime Data](https://torcrime.herokuapp.com/Crime_Data)**')

logger.info(f"Seconds to run: {round(time.process_time() - start_time, 2)}")
streamlit_analytics.stop_tracking()

