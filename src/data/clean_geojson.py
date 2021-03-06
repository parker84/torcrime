import json

with open('./data/raw/shapefile_toronto/Neighbourhood_Crime_Rates_Boundary_File_.json') as json_file:
    data = json.load(json_file)
    for feat in data["features"]:
        feat["properties"]["clean_nbdh_id"] = int(feat["properties"]["Hood_ID"].lstrip("0"))
with open('./src/visualization/viz_data/Neighbourhood_Crime_Rates_Boundary_File_clean.json', "w") as out_file:
    json.dump(data, out_file)