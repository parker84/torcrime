
import pandas as pd
from sqlalchemy import create_engine
from decouple import config

engine = create_engine(config('ENGINE_PATH'))
conn = engine.connect()

df = pd.read_sql("select * from stg.crime_data", conn)
df.to_csv("./data/processed/dash/crime_data.csv")