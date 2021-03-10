import streamlit as st

with st.echo(code_location='below'):
    import pandas as pd
    import numpy as np
    import pydeck as pdk
    import hdbscan
    from pandasql import sqldf
    from plotnine import *
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="toronto_crime_app")

    #-----------------setup
    st.title("Toronto Crime Analysis")
    st.text("Cluster analysis for the crimes chosen within the neighbourhoods chosen")
    st.text("First we'll cluster the crimes together, and remove outliers, then we'll visualize these clusters and finally overlay them on the streets of Toronto")

    crime_df = pd.read_csv(
        "./data/processed/crime_data.csv").rename(columns={"long": "lon"})

    #---------------filtering
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

    #--------------clustering
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
    clusterer.fit(filtered_crime_df[["lon", "lat"]])
    filtered_crime_df["cluster"] = clusterer.labels_
    filtered_crime_df["cluster_prob_assignment"] = clusterer.probabilities_

    # filter out the points that didn't get assigned a cluster
    filtered_crime_df_outliers_removed = filtered_crime_df[filtered_crime_df["cluster"] != -1]
    perc_data_removed_bc_of_outliers = (1 - filtered_crime_df_outliers_removed.shape[0] / filtered_crime_df.shape[0]) * 100
    st.text(f"Percentage of crimes removed because they're considered outliers: {round(perc_data_removed_bc_of_outliers, 2)}% (choosing a lower Minimum Cluster Size will reduce this %")

    #--------------clustering eda
    pysqldf = lambda q: sqldf(q, globals())
    query = f"""
        --sql
        with info_per_cluster as (
            select 
                cluster 
                ,count(1) as n_per_cluster
                ,avg(lat) as avg_lat 
                ,avg(lon) as avg_lon
            from filtered_crime_df_outliers_removed
            group by cluster 
        ), info_per_neighbourhood as (
            select 
                neighbourhood
                ,count(1) as n_per_nbhd
            from filtered_crime_df_outliers_removed
            group by neighbourhood 
        ), info_per_cluster_neighbourhood as (
            select 
                cluster 
                ,count(1) as n_per_cluster_and_neighbourhood
                ,neighbourhood
                ,population
                ,sq_metres / 1000000 as sq_kms 
            from filtered_crime_df_outliers_removed
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
    stats_per_cluster_and_nbhd = pysqldf(query)
    stats_per_cluster = stats_per_cluster_and_nbhd[["n_per_cluster", "cluster", "avg_lat", "avg_lon"]].drop_duplicates()
    
    #-------------extract the address from the lat and long
    addresses = []
    for ix, row in stats_per_cluster[["avg_lat", "avg_lon"]].iterrows():
        address = geolocator.reverse(f"{row.avg_lat}, {row.avg_lon}")
        addresses.append(address[0])
    stats_per_cluster["Address"] = addresses

    #---------------show dataframes
    st.text('Cluster Statistics: (you can hover over the address to see more details)')
    st.dataframe(
        stats_per_cluster[["n_per_cluster", "cluster", "Address", "avg_lat", "avg_lon"]]
        .sort_values(by="n_per_cluster", ascending=False)
    )
    st.text('Cluster/Neighbourhood Statistics:')
    st.dataframe(
        stats_per_cluster_and_nbhd
        .sort_values(by="n_per_cluster", ascending=False)
    )

    #-------visualization
    if stats_per_cluster.shape[0] < 50: # => lets treat this as a str to viz it easier
        filtered_crime_df_outliers_removed["cluster"] = filtered_crime_df_outliers_removed.cluster.astype(str)
        stats_per_cluster["cluster"] = stats_per_cluster["cluster"].astype(str)
    p_clust = ggplot(
        filtered_crime_df_outliers_removed,
        aes("lon", "lat", color="cluster")
    ) + geom_point()
    st.text("Here are the crimes, coloured by their cluster after removing outliers")
    st.pyplot(p_clust.draw())
    p_clust_center = ggplot(
        stats_per_cluster,
        aes("avg_lon", "avg_lat", color="cluster", size="n_per_cluster")
    ) + geom_point()
    st.text("Here are the centers of each cluster, sized by how many crimes occurred in that cluster")
    st.pyplot(p_clust_center.draw())
    p_nbhd = ggplot(
        filtered_crime_df_outliers_removed,
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
                filtered_crime_df_outliers_removed,
                get_position=['lon', 'lat'],
                auto_highlight=True,
                get_radius=10,
                get_fill_color='[180, 0, 200, 140]',
            ),
        ],
    ))
    st.button("Re-run")
    st.text("Code")