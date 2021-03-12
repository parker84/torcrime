import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import math
from plotnine import *
import geopy.distance
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="toronto_crime_app")

#-----------------setup
st.title("Toronto Crime Address Analysis")
st.text("This platform will allow you to investigate crime around a specific address of interest")

crime_df = pd.read_csv(
    "./data/processed/crime_data.csv").rename(columns={"long": "lon"})

#---------------sidebar filtering
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


#------------Filtering to radius around address
address = st.text_input("Enter the address of interest", "1 Dundas st East, Toronto")
walking_mins_str = st.selectbox(
    label="Select Walking Distance Radius (Based on the average walking speed of 5km/h)",
    options=["1 minute", "5 minutes", "10 minutes", "15 minutes", "30 minutes"],
    index=1
)
hours = int(walking_mins_str.split(" ")[0]) / 60
km_radius = round(hours * 5, 3) # we assume 5 km/h walk speed
location = geolocator.geocode(address)
lat, lon = location.latitude, location.longitude
filtered_crime_df["distance_to_address"] = [
    geopy.distance.distance((lat, lon), (row.lat, row.lon)).km
    for ix, row in filtered_crime_df.iterrows()
]
filtered_crime_df_within_radius = (
    filtered_crime_df
    [filtered_crime_df["distance_to_address"] <= km_radius]
    .rename(
        columns={
            "occurrencehour": "Hour of Day",
            "occurrenceyear": "Year",
            "occurrencedayofweek": "Day of Week",
            "crime_type": "Type of Crime"
        }
    )
)
filtered_crime_df_within_radius["Day of Week"] = pd.Categorical(
    filtered_crime_df_within_radius["Day of Week"].str.strip(),
    categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)
n_crimes = filtered_crime_df_within_radius.shape[0]
st.text(f'{n_crimes} Crimes within {walking_mins_str} radius of {address} between {int(crime_df.occurrenceyear.min())} and {int(crime_df.occurrenceyear.max())}')

# #-------------extract the address from the lat and long (too slow)
# addresses = []
# for ix, row in filtered_crime_df_within_radius[["lat", "lon"]].iterrows():
#     address = geolocator.reverse(f"{row.lat}, {row.lon}")
#     addresses.append(address[0])
# filtered_crime_df_within_radius["Address"] = addresses


#------------viz - counts on maps
df_eda_per_address = (
    filtered_crime_df_within_radius
    .groupby(["lat", "lon"])
    .size().reset_index().rename(columns={0:"count"})
)
p = ggplot(
    df_eda_per_address.rename(columns={"lat": "latitude", "lon": "longitude"}),
    aes("longitude", "latitude", size="count")
) + geom_point() + ggtitle(f'Crimes within {walking_mins_str} radius of {address}')
st.pyplot(p.draw())
st.text("Crimes On Toronto Streets (you can zoom/drag)")
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=14,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            filtered_crime_df_within_radius,
            get_position=['lon', 'lat'],
            auto_highlight=True,
            get_radius=5,
            get_fill_color='[180, 0, 200, 140]',
        ),
    ],
))


#------------viz - eda stats
def groupby_var_and_line_chart(df, var):
    df_eda = (
    df
    .groupby(var)
    .size().reset_index().rename(columns={0:"Number of Crimes"})
)
    p = ggplot(
        df_eda,
        aes(var, "Number of Crimes", group=1)
    ) + geom_line() + geom_point() + ggtitle(f'Crimes per {var} within {walking_mins_str} radius of {address}')
    st.pyplot(p.draw())

def groupby_2_vars_and_line_chart(df, variables):
    df_eda = (
    df
    .groupby(variables)
    .size().reset_index().rename(columns={0:"Number of Crimes"})
)
    p = ggplot(
        df_eda,
        aes(variables[0], "Number of Crimes", group=variables[1], color=variables[1])
    ) + geom_line() + geom_point() + ggtitle(f'Crimes within {walking_mins_str} radius of {address}')
    st.pyplot(p.draw())

groupby_var_and_line_chart(filtered_crime_df_within_radius, "Hour of Day")
groupby_var_and_line_chart(filtered_crime_df_within_radius, "Year")
groupby_var_and_line_chart(filtered_crime_df_within_radius, "Day of Week")
groupby_2_vars_and_line_chart(filtered_crime_df_within_radius, ["Hour of Day", "Type of Crime"])
groupby_2_vars_and_line_chart(filtered_crime_df_within_radius, ["Year", "Type of Crime"])
groupby_2_vars_and_line_chart(filtered_crime_df_within_radius, ["Day of Week", "Type of Crime"])


#---------------show dataframes
st.text(f'Crimes within {walking_mins_str} radius of {address} between {int(crime_df.occurrenceyear.min())} and {int(crime_df.occurrenceyear.max())}')
filtered_crime_df_within_radius["Day of Week"] = (
    filtered_crime_df_within_radius["Day of Week"].astype(str)
)
st.dataframe(
    filtered_crime_df_within_radius[[
        "Type of Crime", #"Address", 
        "Year", "Hour of Day", "Day of Week", "premisetype", "neighbourhood"
    ]]
    .sort_values(by=["Year"], ascending=False)
)

st.button("Re-run")
