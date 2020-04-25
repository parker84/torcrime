import os
import pathlib
import re
import plotly.express as px
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

with open("./data/raw/rates/Neighbourhood_Crime_Rates_Boundary_File_.json", "r") as f:
    counties = json.load(f)
df = pd.read_csv("./data/raw/rates/Neighbourhood_Crime_Rates_Boundary_File_.csv",
                dtype={"Hood_ID": str})

YEARS = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]


# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url("dash-logo.png")),
                html.H4(children="Rate of US Poison-Induced Deaths"),
                html.P(
                    id="description",
                    children="† Deaths are classified using the International Classification of Diseases, \
                    Tenth Revision (ICD–10). Drug-poisoning deaths are defined as having ICD–10 underlying \
                    cause-of-death codes X40–X44 (unintentional), X60–X64 (suicide), X85 (homicide), or Y10–Y14 \
                    (undetermined intent).",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=min(YEARS),
                                    marks={
                                        str(year): {
                                            "label": str(year),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for year in YEARS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap of age adjusted mortality rates \
                            from poisonings in year {0}".format(
                                        min(YEARS)
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=(
                                        px.choropleth(df, 
                                            geojson=counties, 
                                            color="Assault_AVG",
                                            locations="OBJECTID", 
                                            featureidkey="properties.OBJECTID",
                                            hover_data=["Neighbourhood"],
                                            color_continuous_scale="Viridis",
                                            scope="north america",
                                        )
                                        .update_geos(showcountries=False, showcoastlines=False, showland=False, fitbounds="locations")
                                        .update_layout(margin={"r":0,"t":0,"l":0,"b":0})
                                    )
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# @app.callback(
#     Output("county-choropleth", "figure"),
#     [Input("years-slider", "value")],
#     [State("county-choropleth", "figure")],
# )
# def display_map(year, figure):
#     cm = dict(zip(BINS, DEFAULT_COLORSCALE))

#     data = [
#         dict(
#             lat=df_lat_lon["Latitude "],
#             lon=df_lat_lon["Longitude"],
#             text=df_lat_lon["Hover"],
#             type="scattermapbox",
#             hoverinfo="text",
#             marker=dict(size=5, color="white", opacity=0),
#         )
#     ]

#     annotations = [
#         dict(
#             showarrow=False,
#             align="right",
#             text="<b>Age-adjusted death rate<br>per county per year</b>",
#             font=dict(color="#2cfec1"),
#             bgcolor="#1f2630",
#             x=0.95,
#             y=0.95,
#         )
#     ]

#     for i, bin in enumerate(reversed(BINS)):
#         color = cm[bin]
#         annotations.append(
#             dict(
#                 arrowcolor=color,
#                 text=bin,
#                 x=0.95,
#                 y=0.85 - (i / 20),
#                 ax=-60,
#                 ay=0,
#                 arrowwidth=5,
#                 arrowhead=0,
#                 bgcolor="#1f2630",
#                 font=dict(color="#2cfec1"),
#             )
#         )

#     if "layout" in figure:
#         lat = figure["layout"]["mapbox"]["center"]["lat"]
#         lon = figure["layout"]["mapbox"]["center"]["lon"]
#         zoom = figure["layout"]["mapbox"]["zoom"]
#     else:
#         lat = (38.72490,)
#         lon = (-95.61446,)
#         zoom = 3.5

#     layout = dict(
#         mapbox=dict(
#             layers=[],
#             accesstoken=mapbox_access_token,
#             style=mapbox_style,
#             center=dict(lat=lat, lon=lon),
#             zoom=zoom,
#         ),
#         hovermode="closest",
#         margin=dict(r=0, l=0, t=0, b=0),
#         annotations=annotations,
#         dragmode="lasso",
#     )

#     base_url = "https://raw.githubusercontent.com/jackparmer/mapbox-counties/master/"
#     for bin in BINS:
#         geo_layer = dict(
#             sourcetype="geojson",
#             source=base_url + str(year) + "/" + bin + ".geojson",
#             type="fill",
#             color=cm[bin],
#             opacity=DEFAULT_OPACITY,
#             # CHANGE THIS
#             fill=dict(outlinecolor="#afafaf"),
#         )
#         layout["mapbox"]["layers"].append(geo_layer)

#     fig = dict(data=data, layout=layout)
#     return fig


# @app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
# def update_map_title(year):
#     return "Heatmap of age adjusted mortality rates \
# 				from poisonings in year {0}".format(
#         year
#     )


if __name__ == "__main__":
    app.run_server(debug=True)
