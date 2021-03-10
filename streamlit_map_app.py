import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.title("Toronto Crime Analysis")

crime_df = pd.read_csv("./data/processed/crime_data.csv").rename(columns={"long": "lon"})

# st.map(crime_df[["lat", "lon"]]) 

st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=43.65,
            longitude=-79.38,
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
               'HexagonLayer',
               data=crime_df.head(100),
               get_position='[lon, lat]',
               radius=200,
            #    elevation_scale=4,
            #    elevation_range=[0, 1000],
            #    pickable=True,
            #    extruded=True,
            ),
#             pdk.Layer(
#                 'ScatterplotLayer',
#                 data=df,
#                 get_position='[lon, lat]',
#                 get_color='[200, 30, 0, 160]',
#                 get_radius=200,
#             ),
        ],
    ))