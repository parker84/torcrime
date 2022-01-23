from src.utils.geocoder import GeoCoder
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from plotnine import *
import geopy.distance
import os
import coloredlogs
import logging
import time
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
    
    def __init__(self, address, walking_mins_str, filtered_crime_df, min_year, max_year, initial_random_addresses):
        self.address = address
        self.walking_mins_str = walking_mins_str
        self.filtered_crime_df = filtered_crime_df
        self.geocoder = GeoCoder()
        self.initial_random_addresses = initial_random_addresses
        self.min_year, self.max_year = min_year, max_year
        self.filter_crime_df_within_radius()

    def filter_crime_df_within_radius(self):
        logger.info("Filtering to radius around address")
        if self.address == 'Enter Address Here (ex: "1 Dundas St"), Toronto':
            self.address = np.random.choice(self.initial_random_addresses)
        hours = int(self.walking_mins_str.split(" ")[0]) / 60
        km_radius = round(hours * 5, 3) # we assume 5 km/h walk speed
        try:
            location = self.geocoder.geocode(self.address)
        except Exception as err:
            logger.warn(f"{err}")
            logger.warn(f"sleeping for 5 secs and trying again")
            time.sleep(5)
            location = self.geocoder.geocode(self.address)
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
        st.markdown(f'Address: `{self.address}`')
        st.markdown(f'Crimes: `{n_crimes}` within {self.walking_mins_str} radius, between {int(self.min_year)} and {int(self.max_year)}')
        self.filtered_crime_df_within_radius = filtered_crime_df_within_radius
    
    def viz_close_neighbourhood_rankings(self):
        neighbourhood_rankings = self._get_neighbourhood_rankings()
        close_nbhds = (
            self.filtered_crime_df_within_radius
            .groupby("neighbourhood").size().reset_index()
            .rename(columns={0: "Crimes Within Radius"})
        )
        close_rankings = (
            neighbourhood_rankings.merge(close_nbhds, how="inner", on="neighbourhood")
            .sort_values(by=["Crimes Within Radius"], ascending=False)
        )
        st.markdown(
            f"""
            #### Ranking of Neighbourhoods Close to You
            The Worst Neighbourhood In Your Radius is in the **{round(close_rankings['Neighbourhood Percentile of Crime'].iloc[0])}th 
            Percentile** For Amount of Crime (100th being the neighbourhood with the most crime)
            """
        )
        st.dataframe(
            close_rankings
            .rename(columns={
                "neighbourhood": "Neighbourhood", 
                "Number of Crimes": "Crimes in Neighbourhood",
                "Neighbourhood Percentile of Crime": "Percentile of Crime",
                "Neighbourhood Percentile of Crimes Per Person": "Percentile of Crimes Per Person",
                "Neighbourhood Percentile of Crimes Per Square Km": "Percentile of Crimes Per Square Km"
            })
            [[
                "Neighbourhood", 
                "Percentile of Crime",
                "Crimes Within Radius",
                "Crimes in Neighbourhood",
                "Percentile of Crimes Per Person", 
                "Percentile of Crimes Per Square Km"
            ]]
        )


    def viz_crime_counts_on_map(self):
        logger.info("Viz Crime Counts on Maps")
        st.markdown("#### Visualizing Crimes Geographically")
        #------------viz - counts on maps
        df_eda_per_address = (
            self.filtered_crime_df_within_radius
            .assign(
                    latitude = self.filtered_crime_df_within_radius.lat.round(4),
                    longitude = self.filtered_crime_df_within_radius.lon.round(4)
            )
            .groupby(["latitude", "longitude"])
            .neighbourhood
            .agg(["max", "size"])
            .reset_index().rename(columns={"max":"neighbourhood", "size": "Number of Crimes"})
        )
        plot_color = st.selectbox(
            label="Colour the Graph Below by:",
            options=["Neighbourhood", "Number of Crimes"],
            index=0
        )
        p = ggplot(
            df_eda_per_address.rename(columns={"neighbourhood": "Neighbourhood"}),
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
                    'HeatmapLayer',
                    self.filtered_crime_df_within_radius[["lat", "lon"]],
                    get_position=['lon', 'lat'],
                    auto_highlight=True,
                    get_radius=5,
                    get_fill_color='[180, 0, 200, 140]',
                ),
            ],
        ))

    def viz_eda_plots(self):
        st.markdown("#### Visualizing Crimes By Time")
        self._groupby_var_and_line_chart(self.filtered_crime_df_within_radius, "Hour of Day")
        self._groupby_var_and_line_chart(self.filtered_crime_df_within_radius, "Year")
        self._groupby_var_and_line_chart(self.filtered_crime_df_within_radius, "Day of Week")
        self._groupby_2_vars_and_line_chart(self.filtered_crime_df_within_radius, ["Hour of Day", "Type of Crime"])
        self._groupby_2_vars_and_line_chart(self.filtered_crime_df_within_radius, ["Year", "Type of Crime"])
        self._groupby_2_vars_and_line_chart(self.filtered_crime_df_within_radius, ["Day of Week", "Type of Crime"])

    def show_dataframes(self):
        st.markdown("#### Crime Details Within Radius")
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

    def _get_neighbourhood_rankings(self):
        neighbourhood_stats = (
            self.filtered_crime_df
            .groupby(["neighbourhood", "population", "sq_metres"])
            .size().reset_index()
            .rename(columns={0: "Number of Crimes"})
        )
        assert neighbourhood_stats.shape[0] == neighbourhood_stats.neighbourhood.unique().shape[0], "dups in primay key"
        neighbourhood_stats["Crimes Per Person"] = (
            neighbourhood_stats["Number of Crimes"] / neighbourhood_stats.population
        )
        neighbourhood_stats["Crimes Per Square Km"] = (
            neighbourhood_stats["Number of Crimes"] / (neighbourhood_stats.sq_metres * 1e-6)
        )
        neighbourhood_stats["Neighbourhood Percentile of Crime"] = (neighbourhood_stats["Number of Crimes"].rank(pct=True)*100).round(2)
        neighbourhood_stats["Neighbourhood Percentile of Crimes Per Person"] = (neighbourhood_stats["Crimes Per Person"].rank(pct=True)*100).round(2)
        neighbourhood_stats["Neighbourhood Percentile of Crimes Per Square Km"] = (neighbourhood_stats["Crimes Per Square Km"].rank(pct=True)*100).round(2)
        return neighbourhood_stats