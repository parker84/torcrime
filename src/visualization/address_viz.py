import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import math
from plotnine import *
import geopy.distance
import os
import coloredlogs
import logging
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)

#------------Helpers
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
class AddressViz():
    
    def __init__(self, filtered_crime_df, geolocator, min_year, max_year):
        self.filtered_crime_df = filtered_crime_df
        self.geolocator = geolocator
        self.min_year, self.max_year = min_year, max_year
        self.show_intro_text()
        self.filter_crime_df_within_radius()

    def show_intro_text(self):
        st.markdown("#### This platform will allow you to investigate crime around a specific address of interest")

    def filter_crime_df_within_radius(self):
        logger.info("Filtering to radius around address")
        self.address = st.text_input("Enter the address of interest", "1 Dundas st East, Toronto")
        self.walking_mins_str = st.selectbox(
            label="Select Walking Distance Radius (Based on the average walking speed of 5km/h)",
            options=["1 minute", "5 minutes", "10 minutes", "15 minutes", "30 minutes"],
            index=1
        )
        hours = int(self.walking_mins_str.split(" ")[0]) / 60
        km_radius = round(hours * 5, 3) # we assume 5 km/h walk speed
        location = self.geolocator.geocode(self.address)
        self.lat, self.lon = location.latitude, location.longitude
        self.filtered_crime_df["distance_to_address"] = calc_distances(self.filtered_crime_df, self.lat, self.lon)
        filtered_crime_df_within_radius = (
            self.filtered_crime_df
            [self.filtered_crime_df["distance_to_address"] <= km_radius]
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
        st.markdown(f'### Crime Analysis Report')
        st.text(f'{n_crimes} Crimes within {self.walking_mins_str} radius of {self.address} between {int(self.min_year)} and {int(self.max_year)}')
        self.filtered_crime_df_within_radius = filtered_crime_df_within_radius
                
    def viz_crime_counts_on_map(self):
        logger.info("Viz Crime Counts on Maps")
        #------------viz - counts on maps
        df_eda_per_address = (
            self.filtered_crime_df_within_radius
            .groupby(["lat", "lon", "neighbourhood"])
            .size().reset_index().rename(columns={0:"Number of Crimes"})
        )
        plot_color = st.selectbox(
            label="Colour the Graph Below by:",
            options=["Neighbourhood", "Number of Crimes"],
            index=0
        )
        p = ggplot(
            df_eda_per_address.rename(columns={"lat": "latitude", "lon": "longitude", "neighbourhood": "Neighbourhood"}),
            aes(
                "longitude", "latitude", 
                size="Number of Crimes", 
                fill=plot_color,
                color=plot_color
            )
        ) + geom_point() + ggtitle(f'Crimes within {self.walking_mins_str} radius of {self.address}')
        st.pyplot(p.draw())
        st.text("Crimes On Toronto Streets (you can zoom/drag)")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=self.lat,
                longitude=self.lon,
                zoom=14,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    self.filtered_crime_df_within_radius,
                    get_position=['lon', 'lat'],
                    auto_highlight=True,
                    get_radius=5,
                    get_fill_color='[180, 0, 200, 140]',
                ),
            ],
        ))

    def viz_eda_plots(self):
        self._groupby_var_and_line_chart(self.filtered_crime_df_within_radius, "Hour of Day")
        self._groupby_var_and_line_chart(self.filtered_crime_df_within_radius, "Year")
        self._groupby_var_and_line_chart(self.filtered_crime_df_within_radius, "Day of Week")
        self._groupby_2_vars_and_line_chart(self.filtered_crime_df_within_radius, ["Hour of Day", "Type of Crime"])
        self._groupby_2_vars_and_line_chart(self.filtered_crime_df_within_radius, ["Year", "Type of Crime"])
        self._groupby_2_vars_and_line_chart(self.filtered_crime_df_within_radius, ["Day of Week", "Type of Crime"])

    def show_dataframes(self):
        st.text(f'Crimes within {self.walking_mins_str} radius of {self.address} between {int(self.min_year)} and {int(self.max_year)}')
        self.filtered_crime_df_within_radius["Day of Week"] = (
            self.filtered_crime_df_within_radius["Day of Week"].astype(str)
        )
        st.dataframe(
            self.filtered_crime_df_within_radius[[
                "Type of Crime", #"Address", 
                "Year", "Hour of Day", "Day of Week", "premisetype", "neighbourhood"
            ]]
            .sort_values(by=["Year"], ascending=False)
        )
    def _groupby_var_and_line_chart(self, df, var):
        df_eda = (
        df
        .groupby(var)
        .size().reset_index().rename(columns={0:"Number of Crimes"})
    )
        p = ggplot(
            df_eda,
            aes(var, "Number of Crimes", group=1)
        ) + geom_line() + geom_point() + ggtitle(f'Crimes per {var} within {self.walking_mins_str} radius of {self.address}')
        st.pyplot(p.draw())

    def _groupby_2_vars_and_line_chart(self, df, variables):
        df_eda = (
        df
        .groupby(variables)
        .size().reset_index().rename(columns={0:"Number of Crimes"})
    )
        p = ggplot(
            df_eda,
            aes(variables[0], "Number of Crimes", group=variables[1], color=variables[1])
        ) + geom_line() + geom_point() + ggtitle(f'Crimes within {self.walking_mins_str} radius of {self.address}')
        st.pyplot(p.draw())