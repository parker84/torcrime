# Vizing Crime Rates for Toronto


1. download the shapefiles: http://data.torontopolice.on.ca/datasets/neighbourhood-crime-rates-boundary-file-/data
2. convert the shapefiles to json:
    - unzip these move into this folder and execute the steps here: https://ben.balter.com/2013/06/26/how-to-convert-shapefiles-to-geojson-for-use-on-github/
   - ex: ogr2ogr -f GeoJSON -t_srs crs:84 ./data/raw/Neighbourhood_Crime_Rates_Boundary_File_.json ./data/raw/shapefile_toronto/Neighbourhood_Crime_Rates_Boundary_File_.shp
   - save to json not geo json
3. we cleaned up the neighbourhood names too:
```py
import json
with open('./data/raw/shapefile_toronto/Neighbourhood_Crime_Rates_Boundary_File_.json') as json_file:
    data = json.load(json_file)
    for feat in data["features"]:
        feat["properties"]["clean_nbdh_id"] = int(feat["properties"]["Hood_ID"].lstrip("0"))
with open('./data/raw/shapefile_toronto/Neighbourhood_Crime_Rates_Boundary_File_clean.json', "w") as out_file:
    json.dump(data, out_file)
```
4. viz:
```py
with open("./data/raw/shapefile_toronto/Neighbourhood_Crime_Rates_Boundary_File_clean.json", "r") as f:
    counties = json.load(f)
fig=(
    px.choropleth(preds_per_nbhd_id, 
        geojson=counties, 
        color="expected_crimes_per_hour_per_sq_km",
        locations="nbhd_id", 
        featureidkey="properties.clean_nbdh_id",
        hover_data=["neighbourhood"],
        color_continuous_scale="Viridis",
        scope="north america",
    )
    .update_geos(showcountries=False, showcoastlines=False, showland=False, showlakes=False, fitbounds="locations")
    .update_layout(margin={"r":0,"t":0,"l":0,"b":0}
)
fig.show()
```