import pandas as pd
from sqlalchemy import create_engine
from decouple import config

engine = create_engine(config('ENGINE_PATH'))
conn = engine.connect()


def load():
    mci_df = pd.read_csv("./data/raw/mci/MCI_2014_to_2019.csv")
    nbhd_df = pd.read_csv("./data/raw/rates/Neighbourhood_Crime_Rates_Boundary_File_.csv")

    mci_df.to_sql(con=conn, name="mci_data", schema="src", if_exists="replace", index=True)
    nbhd_df.to_sql(con=conn, name="nbhd_data", schema="src", if_exists="replace", index=True)

if __name__ == "__main__":
    load()