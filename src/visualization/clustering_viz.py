import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import math
from plotnine import *
import geopy.distance
from pandasql import sqldf
import os
import hdbscan
import coloredlogs
import logging
logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)



class ClusteringViz():

    def __init__(self, filtered_crime_df, geolocator):
        self.filtered_crime_df = filtered_crime_df
        self.geolocator = geolocator
        self.show_title()
        self.filter_to_neighbourhoods()

    def show_title(self):
        st.title("Toronto Crime Analysis")
        st.text("Cluster analysis for the crimes chosen within the neighbourhoods chosen")
        st.text("First we'll cluster the crimes together, and remove outliers, then we'll visualize these clusters and finally overlay them on the streets of Toronto")

    def filter_to_neighbourhoods(self):
        nbhd_options = st.sidebar.multiselect(
            label="Choose Neighbourhoods (May not render with all neighbourhoods chosen)",
            options=self.filtered_crime_df.neighbourhood.unique().tolist(),
            default=[
                'Moss Park (73)',
                'Church-Yonge Corridor (75)',
                'Bay Street Corridor (76)',
                'Kensington-Chinatown (78)',
                'Waterfront Communities-The Island (77)'
            ]
        )
        self.filtered_crime_df_to_nbhds = self.filtered_crime_df[self.filtered_crime_df.neighbourhood.isin(nbhd_options)]
    
    def cluster_crimes_and_remove_outliers(self):
        logger.info("Clustering")
        st.sidebar.markdown('### Choose hdbscan parameters')
        st.sidebar.text("(see here for more details: https://hdbscan.readthedocs.io/en/latest/parameter_selection.html)")
        min_cluster_size = st.sidebar.selectbox(
            label="Choose Minimum Cluster Size",
            options=[10, 50, 100, 200, 400],
            index=2
        )

        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size
        )
        clusterer.fit(self.filtered_crime_df_to_nbhds[["lon", "lat"]])
        self.filtered_crime_df_to_nbhds["cluster"] = clusterer.labels_
        self.filtered_crime_df_to_nbhds["cluster_prob_assignment"] = clusterer.probabilities_

        # filter out the points that didn't get assigned a cluster
        self.filtered_crime_df_to_nbhds_outliers_removed = self.filtered_crime_df_to_nbhds[self.filtered_crime_df_to_nbhds["cluster"] != -1]
        perc_data_removed_bc_of_outliers = (1 - self.filtered_crime_df_to_nbhds_outliers_removed.shape[0] / self.filtered_crime_df_to_nbhds.shape[0]) * 100
        st.text(f"Percentage of crimes removed because they're considered outliers: {round(perc_data_removed_bc_of_outliers, 2)}% (choosing a lower Minimum Cluster Size will reduce this %")

    def set_stats_per_cluster(self):
        global filtered_crime_df_to_nbhds_outliers_removed
        filtered_crime_df_to_nbhds_outliers_removed = self.filtered_crime_df_to_nbhds_outliers_removed
        # import ipdb; ipdb.set_trace()
        logger.info("EDA per cluster")
        pysqldf = lambda q: sqldf(q, globals())
        query = f"""
            --sql
            with info_per_cluster as (
                select 
                    cluster 
                    ,count(1) as n_per_cluster
                    ,avg(lat) as avg_lat 
                    ,avg(lon) as avg_lon
                from filtered_crime_df_to_nbhds_outliers_removed
                group by cluster 
            ), info_per_neighbourhood as (
                select 
                    neighbourhood
                    ,count(1) as n_per_nbhd
                from filtered_crime_df_to_nbhds_outliers_removed
                group by neighbourhood 
            ), info_per_cluster_neighbourhood as (
                select 
                    cluster 
                    ,count(1) as n_per_cluster_and_neighbourhood
                    ,neighbourhood
                    ,population
                    ,sq_metres / 1000000 as sq_kms 
                from filtered_crime_df_to_nbhds_outliers_removed
                group by cluster, neighbourhood
            ) 
            select 
                clust.n_per_cluster
                ,nbhd.n_per_nbhd
                ,clust_and_nbhd.*
                ,clust.avg_lat
                ,clust.avg_lon
            from info_per_cluster_neighbourhood as clust_and_nbhd 
            left join info_per_cluster as clust on 
                clust_and_nbhd.cluster = clust.cluster
            left join info_per_neighbourhood as nbhd on 
                clust_and_nbhd.neighbourhood = nbhd.neighbourhood
            ;
        """
        self.stats_per_cluster_and_nbhd = pysqldf(query)
        self.stats_per_cluster = self.stats_per_cluster_and_nbhd[["n_per_cluster", "cluster", "avg_lat", "avg_lon"]].drop_duplicates()
        
    def add_addresses_per_cluster(self):
        logger.info("Getting addresses")
        addresses = []
        for ix, row in self.stats_per_cluster[["avg_lat", "avg_lon"]].iterrows():
            address = self.geolocator.reverse(f"{row.avg_lat}, {row.avg_lon}")
            addresses.append(address[0])
        self.stats_per_cluster["Address"] = addresses
    

    def show_dataframes(self):
        logger.info("Viz dfs")
        st.text('Cluster Statistics: (you can hover over the address to see more details)')
        st.dataframe(
            self.stats_per_cluster[["n_per_cluster", "cluster", "Address", "avg_lat", "avg_lon"]]
            .sort_values(by="n_per_cluster", ascending=False)
        )
        st.text('Cluster/Neighbourhood Statistics:')
        st.dataframe(
            self.stats_per_cluster_and_nbhd
            .sort_values(by="n_per_cluster", ascending=False)
        )

    def viz_clusters(self):
        logger.info("Viz clusters")
        if self.stats_per_cluster.shape[0] < 50: # => lets treat this as a str to viz it easier
            self.filtered_crime_df_to_nbhds_outliers_removed["cluster"] = self.filtered_crime_df_to_nbhds_outliers_removed.cluster.astype(str)
            self.stats_per_cluster["cluster"] = self.stats_per_cluster["cluster"].astype(str)
        p_clust = ggplot(
            self.filtered_crime_df_to_nbhds_outliers_removed,
            aes("lon", "lat", color="cluster")
        ) + geom_point()
        st.text("Here are the crimes, coloured by their cluster after removing outliers")
        st.pyplot(p_clust.draw())
        p_clust_center = ggplot(
            self.stats_per_cluster,
            aes("avg_lon", "avg_lat", color="cluster", size="n_per_cluster")
        ) + geom_point()
        st.text("Here are the centers of each cluster, sized by how many crimes occurred in that cluster")
        st.pyplot(p_clust_center.draw())
        p_nbhd = ggplot(
            self.filtered_crime_df_to_nbhds_outliers_removed,
            aes("lon", "lat", color="neighbourhood")) + geom_point()
        st.text("Here are the crimes, coloured by their neighbourhood after removing outliers")
        st.pyplot(p_nbhd.draw())

        st.text("Here are the crimes on the streets of Toronto, you can use this to isolate the locations of each cluster represented above")
        st.text("(you can zoom/drag on this graph)")
        st.pydeck_chart(pdk.Deck(
            initial_view_state=pdk.ViewState(
                latitude=43.65,
                longitude=-79.38,
                zoom=12,
            ),
            layers=[
                pdk.Layer(
                    'ScatterplotLayer',
                    self.filtered_crime_df_to_nbhds_outliers_removed,
                    get_position=['lon', 'lat'],
                    auto_highlight=True,
                    get_radius=10,
                    get_fill_color='[180, 0, 200, 140]',
                ),
            ],
        ))


            

            

