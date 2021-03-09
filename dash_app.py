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

# with open(os.path.join(
#             config("PYTHONPATH"),
#             "./src/visualization/data/raw/shapefile_toronto/Neighbourhood_Crime_Rates_Boundary_File_clean.json"), 
#         "r") as f:
#     counties = json.load(f)
# df = pd.read_csv(os.path.join(
#             config("PYTHONPATH"),
#             "./src/visualization/data/processed/crime_data.csv"))

with open("./data/processed/dash/Neighbourhood_Crime_Rates_Boundary_File_clean.json", "r") as f:
    counties = json.load(f)
df = pd.read_csv("./data/processed/dash/crime_data.csv")

YEARS = [2014, 2015, 2016, 2017, 2018, 2019]
CRIME_OPTIONS = df.crime_type.unique().tolist()
PREMISES = df.premisetype.unique().tolist()
DAYS_OF_WEEK = [
    "Monday", "Tuesday", "Wednesday", "Thursday", 
    "Friday", "Saturday", "Sunday"
]
HOURS_OF_DAY = list(range(25))

model = AvgModel()
predicter = Predict(df, model)
predicter.filter_df(
            premises=["Outside"], 
            crimes=["Assault"], 
            max_year=2019, 
            min_year=2014, 
            min_hour=0,
            max_hour=24,
            days_of_week=DAYS_OF_WEEK
)
preds_per_km = predicter.predict_cases_per_sq_km_per_nbhd_per_hour()
assert preds_per_km.shape[0] == len(counties["features"])
preds_per_10k_people = predicter.predict_cases_per_10k_people_per_nbhd_per_hour()
assert preds_per_10k_people.shape[0] == len(counties["features"])

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
                                    "Estimating the number of crimes per hour occurring by neighbourhood", style={"margin-top": "0px"}
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
                                dcc.RangeSlider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=[min(YEARS), max(YEARS)],
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
                            id="hour-of-day-slider-container",
                            children=[
                                html.P(
                                    id="hours-slider-text",
                                    children="Drag the slider to change the hour of day:",
                                ),
                                dcc.RangeSlider(
                                    id="hours-slider",
                                    min=min(HOURS_OF_DAY),
                                    max=max(HOURS_OF_DAY),
                                    value=[min(HOURS_OF_DAY), max(HOURS_OF_DAY)],
                                    marks={
                                        str(hour): {
                                            "label": str(hour),
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for hour in HOURS_OF_DAY
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="day-of-week-slider-container",
                            children=[
                                html.P(
                                    id="day-slider-text",
                                    children="Drag the slider to change the day of week:",
                                ),
                                dcc.RangeSlider(
                                    id="day-slider",
                                    min=0,
                                    max=len(DAYS_OF_WEEK)-1,
                                    value=[0, len(DAYS_OF_WEEK)],
                                    marks={
                                        i : {
                                            "label": DAYS_OF_WEEK[i],
                                            "style": {"color": "#7fafdf"},
                                        }
                                        for i in range(len(DAYS_OF_WEEK))
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="crime-checklist-container",
                            children=[
                                html.P(
                                    id="crime-checks-text",
                                    children="Choose your crime types of interest:",
                                ),
                                dcc.Checklist(
                                    id="crime-checker",
                                    options=[
                                        {'label': crime, 'value': crime}
                                        for crime in CRIME_OPTIONS
                                    ],
                                    value=['Assault']
                                ), 
                            ],
                        ),
                        html.Div(
                            id="premise-checklist-container",
                            children=[
                                html.P(
                                    id="premise-checks-text",
                                    children="Choose your premise types of interest:",
                                ),
                                dcc.Checklist(
                                    id="premise-checker",
                                    options=[
                                        {'label': premise, 'value': premise}
                                        for premise in PREMISES
                                    ],
                                    value=['Outside']
                                ), 
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                   f"Heatmap of estimated number of Crimes per hour\
                                        occuring in a given square km of each neihbourhood",
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=(
                                        px.choropleth(preds_per_km, 
                                            geojson=counties, 
                                            color="expected_crimes_per_hour_per_sq_km",
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
                        html.Div(
                            id="heatmap-per-person-container",
                            children=[
                                html.P(
                                   f"Heatmap of estimated number of Crimes per hour\
                                        per 10,000 people in each neighbourhood",
                                    id="heatmap-per-person-title",
                                ),
                                dcc.Graph(
                                    id="choropleth-per-person",
                                    figure=(
                                        px.choropleth(preds_per_10k_people, 
                                            geojson=counties, 
                                            color="expected_crimes_per_hour_per_10k_people",
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
    [
        Input("years-slider", "value"), 
        Input("hours-slider", "value"),
        Input("day-slider", "value"),
        Input("crime-checker", "value"),
        Input("premise-checker", "value")
    ],
    [State("county-choropleth", "figure")],
)
def display_map(years, hours, days, crimes, premises, figure):
    model = AvgModel()
    predicter = Predict(df, model)
    predicter.filter_df(
                premises=premises,
                crimes=crimes, 
                max_year=years[1], 
                min_year=years[0], 
                min_hour=hours[0],
                max_hour=hours[1],
                days_of_week=DAYS_OF_WEEK[days[0]:days[1]]
    )
    preds_per_km = predicter.predict_cases_per_sq_km_per_nbhd_per_hour()
    assert preds_per_km.shape[0] == len(counties["features"])
    fig=(
        px.choropleth(preds_per_km, 
            geojson=counties, 
            color="expected_crimes_per_hour_per_sq_km",
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
    Output("choropleth-per-person", "figure"),
    [
        Input("years-slider", "value"), 
        Input("hours-slider", "value"),
        Input("day-slider", "value"),
        Input("crime-checker", "value"),
        Input("premise-checker", "value")
    ],
    [State("choropleth-per-person", "figure")],
)
def display_map(years, hours, days, crimes, premises, figure):
    model = AvgModel()
    predicter = Predict(df, model)
    predicter.filter_df(
                premises=premises,
                crimes=crimes, 
                max_year=years[1], 
                min_year=years[0], 
                min_hour=hours[0],
                max_hour=hours[1],
                days_of_week=DAYS_OF_WEEK[days[0]:days[1]]
    )
    preds_per_km = predicter.predict_cases_per_10k_people_per_nbhd_per_hour()
    assert preds_per_km.shape[0] == len(counties["features"])
    fig=(
        px.choropleth(preds_per_km, 
            geojson=counties, 
            color="expected_crimes_per_hour_per_10k_people",
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
    return f"Heatmap of estimated number of Crimes per hour\
            occuring in a given square km of each neihbourhood"


if __name__ == "__main__":
    # app.run_server(debug=True, port=8053)
    app.run_server()
