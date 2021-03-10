import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.title("Toronto Crime Analysis")
st.text("Granular analysis of crime within the neighbourhoods chosen")

crime_df = pd.read_csv(
    "./data/processed/crime_data.csv").rename(columns={"long": "lon"})

st.sidebar.markdown('### Choose Your Filters')
nbhd_options = st.sidebar.multiselect(
    label="Choose Neighbourhoods (May not render with all neighbourhoods chosen)",
    options=crime_df.neighbourhood.unique().tolist(),
    default=[
        'Moss Park (73)',
        'Church-Yonge Corridor (75)',
        'Bay Street Corridor (76)',
        'Kensington-Chinatown (78)',
        'Waterfront Communities-The Island (77)'
    ]
)
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

filtered_crime_df = crime_df[crime_df.neighbourhood.isin(nbhd_options)]
filtered_crime_df = filtered_crime_df[filtered_crime_df.crime_type.isin(
    crime_options)]
filtered_crime_df = filtered_crime_df[filtered_crime_df.premisetype.isin(
    location_options)]



st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=43.65,
        longitude=-79.38,
        zoom=12,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=filtered_crime_df,
            get_position='[lon, lat]',
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
        )
    ],
))

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=43.65,
        longitude=-79.38,
        zoom=12,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            filtered_crime_df,
            get_position=['lon', 'lat'],
            auto_highlight=True,
            get_radius=25,
            get_fill_color='[180, 0, 200, 140]',
        ),
    ],
))