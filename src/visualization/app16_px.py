import plotly.express as px
import pandas as pd

# import json
# from urllib.request import urlopen


# df = px.data.election()
# geojson = px.data.election_geojson()
# import ipdb; ipdb.set_trace()

import json
with open("./data/raw/rates/Neighbourhood_Crime_Rates_Boundary_File_.json", "r") as f:
    counties = json.load(f)

df = pd.read_csv("./data/raw/rates/Neighbourhood_Crime_Rates_Boundary_File_.csv",
                dtype={"Hood_ID": str})
# df["AREA_S_CD"] = df.Hood_ID 

# with urlopen("https://github.com/jasonicarter/toronto-geojson/blob/master/toronto_crs84.geojson") as f:
#     geo_tor = json.load(f)
# geo_tor = json.load(f)
# import pygeoj
# import ipdb; ipdb.set_trace()

# testfile = pygeoj.load("https://github.com/jasonicarter/toronto-geojson/blob/master/toronto_crs84.geojson")


# fig = px.choropleth(df, 
#                     geojson="./data/raw/rates/Neighbourhood_Crime_Rates_Boundary_File_.geojson", 
#                     color="Assault_AVG",
#                     # locations="Neighbourhood", featureidkey="Hood_ID",
#                     # locations="Hood_ID", 
#                     locations="OBJECTID", 
#                     # featureidkey="properties.Hood_ID",
#                     # featureidkey="properties.OBJECTID",
#                     featureidkey="features.properties.OBJECTID",
#                     # featureidkey="AREA_S_CD",
#                     scope="north america",
#                     hover_data=["Neighbourhood"]
#                     color_continuous_scale="Viridis",
#                         range_color=(0, 12),
#                    )

fig = px.choropleth(df, 
                    geojson=counties, 
                    # locations='fips', 
                    # color='unemp',
                    color="Assault_AVG",
                    locations="OBJECTID", 
                    featureidkey="properties.OBJECTID",
                    hover_data=["Neighbourhood"],
                    color_continuous_scale="Viridis",
                    # range_color=(0, 12),
                    scope="north america",
                    # labels={'unemp':'unemployment rate'}
                    # center={"lat":-79.391603880596435, "lon":43.680914175011935}
                    )
fig.update_geos(showcountries=False, showcoastlines=False, showland=False, fitbounds="locations")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
# fig.update_geos(fitbounds="locations", visible=False)
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# fig.show()


import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

app.run_server(debug=True)  # Turn off reloader if inside Jupyter