import streamlit as st
from src.models.averaging_model import AvgModel
from src.models.predict_model import Predict
import plotly.express as px
import numpy as np


class CompareNeighbourhoods():


    def __init__(self, filtered_crime_df, counties):
        self.filtered_crime_df = filtered_crime_df
        self.show_intro_text()
        self.counties = counties
        model = AvgModel()
        self.predicter = Predict(filtered_crime_df, model)
        self.filter_df_by_time()

    def show_intro_text(self):
        st.markdown("#### This dashboard will allow you to compare crime rates between different neighbourhoods")

    def filter_df_by_time(self):
        year_range = st.slider("Year Range To Investigate", 2014, 2020, (2014, 2020))
        hour_range = st.slider("Hour of Day Range To Investigate", 0, 24, (0, 24))
        days = st.multiselect(
            label="Days of Week To Investigate",
            options=[
                "Monday", "Tuesday", "Wednesday", "Thursday", 
                "Friday", "Saturday", "Sunday"
            ],
            default=[
                "Monday", "Tuesday", "Wednesday", "Thursday", 
                "Friday", "Saturday", "Sunday"
            ]
        )

        all_premises = self.filtered_crime_df.premisetype.unique()
        all_crimes = self.filtered_crime_df.crime_type.unique()
        self.predicter.filter_df(
                premises=all_premises,
                crimes=all_crimes, 
                max_year=year_range[1], 
                min_year=year_range[0], 
                min_hour=hour_range[0],
                max_hour=hour_range[1],
                days_of_week=days
        )

    def viz(self):
        viz_type = st.selectbox(
            label="Choose Your Visualization Type",
            options=[
                "Crime Counts Per Neighhourhood", 
                "Estimated Probability of Crime Per Hour Per 10k People", 
                "Estimated Probability of Crime Per Hour Per km"
            ],
            index=0
        )
        if viz_type == "Crime Counts Per Neighhourhood":
            self._viz_counts()
        elif viz_type == "Estimated Probability of Crime Per Hour Per 10k People":
            self._viz_per_10k()
        elif viz_type == "Estimated Probability of Crime Per Hour Per km":
            self._viz_per_km()

    def _viz_counts(self):
        counts = self.predicter.get_num_crimes()
        assert counts.shape[0] >= len(self.counties["features"])
        fig=(
            px.choropleth(counts, 
                geojson=self.counties, 
                color="Number of Crimes",
                locations="nbhd_id", 
                featureidkey="properties.clean_nbdh_id",
                hover_data=["neighbourhood"],
                color_continuous_scale="Viridis",
                scope="north america",
            )
            .update_geos(showcountries=False, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
            .update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        )
        st.plotly_chart(fig)
        st.dataframe(
            counts
            .rename(columns={
                "neighbourhood": "Neighbourhood"
            })
            .sort_values(by=["Number of Crimes"], ascending=False)
            .assign(Rank=np.arange(counts.shape[0])+1)
            [[
                "Rank", "Number of Crimes", "Neighbourhood"
            ]]
        )

    def _viz_per_10k(self):
        preds_per_10k = self.predicter.predict_cases_per_10k_people_per_nbhd_per_hour()
        assert abs(preds_per_10k.shape[0] - len(self.counties["features"])) < 2
        fig=(
            px.choropleth(preds_per_10k, 
                geojson=self.counties, 
                color="Probability of Crime",
                locations="nbhd_id", 
                featureidkey="properties.clean_nbdh_id",
                hover_data=["neighbourhood"],
                color_continuous_scale="Viridis",
                scope="north america",
            )
            .update_geos(showcountries=False, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
            .update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        )
        st.plotly_chart(fig)
        st.dataframe(
            preds_per_10k
            .rename(columns={
                "crimes_counts_per_nbhd": "Number of Crimes",
                "population": "Population",
                "neighbourhood": "Neighbourhood"
            })
            .sort_values(by=["Probability of Crime"], ascending=False)
            .assign(Rank=np.arange(preds_per_10k.shape[0])+1)
            [[
                "Rank", "Probability of Crime", "Neighbourhood", "Number of Crimes", "Population"
            ]]
        )

    def _viz_per_km(self):
        preds_per_km = self.predicter.predict_cases_per_sq_km_per_nbhd_per_hour()
        assert abs(preds_per_km.shape[0] - len(self.counties["features"])) < 2

        fig=(
            px.choropleth(preds_per_km, 
                geojson=self.counties, 
                color="Probability of Crime",
                locations="nbhd_id", 
                featureidkey="properties.clean_nbdh_id",
                hover_data=["neighbourhood"],
                color_continuous_scale="Viridis",
                scope="north america",
            )
            .update_geos(showcountries=False, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
            .update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        )
        st.plotly_chart(fig)
        preds_per_km["Square Kms"] = preds_per_km["sq_metres"] * 1e-6
        st.dataframe(
            preds_per_km
            .rename(columns={
                "crimes_counts_per_nbhd": "Number of Crimes",
                "neighbourhood": "Neighbourhood"
            })
            .sort_values(by=["Probability of Crime"], ascending=False)
            .assign(Rank=np.arange(preds_per_km.shape[0])+1)
            [[
                "Rank", "Probability of Crime", "Neighbourhood", "Number of Crimes", "Square Kms"
            ]]
        )