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
from src.models.predict_model import Predict
from src.models.averaging_model import AvgModel

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

with open("./data/raw/shapefile_toronto/Neighbourhood_Crime_Rates_Boundary_File_clean.json", "r") as f:
    counties = json.load(f)
df = pd.read_csv("./data/processed/crime_data.csv")

YEARS = [2014, 2015, 2016, 2017, 2018, 2019]
CRIME_OPTIONS = [
    "Assault",
    "Robbery"
]
PREMISES = [
    "Outside"
]

model = AvgModel()
predicter = Predict(df, model)
predicter.filter_df(
            ["Outdoor"],
            ["Assualt"],
            2019, 2014
)
preds = predicter.predict_cases_per_sq_km_per_nbhd_per_day()
assert preds.shape[0] == len(counties["features"])

# App layout

app.layout = html.Div(
    id="root",
    children=[
                html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("dash-logo.png"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Crime Rates in Toronto",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Estimating probability of crimes occurring by neighbourhood, year, day of week, premise type and time of day", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
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
                                    value=max(YEARS),
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
                                    f"Heatmap of estimated probability of {CRIME_OPTIONS[0]}\
                            occuring in a given square foot of each neihbourhood in year {min(YEARS)}",
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=(
                                        px.choropleth(preds, 
                                            geojson=counties, 
                                            color="expected_crimes_per_day_per_sq_km",
                                            locations="nbhd_id", 
                                            featureidkey="properties.clean_nbdh_id",
                                            hover_data=["neighbourhood"],
                                            color_continuous_scale="Viridis",
                                            scope="north america",
                                        )
                                        .update_geos(showcountries=False, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
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


@app.callback(
    Output("county-choropleth", "figure"),
    [Input("years-slider", "value")],
    [State("county-choropleth", "figure")],
)
def display_map(year, figure):
    # TODO: integrate w predict_model
    # df_filt = 
    fig=(
        px.choropleth(preds, 
            geojson=counties, 
            color="expected_crimes_per_day_per_sq_km",
            locations="nbhd_id", 
            featureidkey="properties.clean_nbdh_id",
            hover_data=["neighbourhood"],
            color_continuous_scale="Viridis",
            scope="north america",
        )
        .update_geos(showcountries=False, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
        .update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    )
    return fig


@app.callback(
    Output("heatmap-title", "children"), 
    [
        Input("years-slider", "value"), 
        # Input("crime-dropdown", "value")
    ])
def update_map_title(year):#, crime):
    # TODO: get the crime droppddown
    crime="Assaualt"
    return f"Heatmap of estimated probability of {crime}\
                            occuring in a given square foot of each neihbourhood in year {year}"


if __name__ == "__main__":
    app.run_server(debug=True)
