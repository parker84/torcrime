import unittest
from src.models.averaging_model import AvgModel
import pandas as pd
from sqlalchemy import create_engine
from decouple import config
from src.utils.logger import init_logger
engine = create_engine(config('ENGINE_PATH'))
conn = engine.connect()


class TestCrimeData(unittest.TestCase):

    df = pd.read_sql(
            "select * from stg.crime_data", 
            con=conn)
    logger = init_logger("TestCrimeData")  
    df_desc = df.describe()
    df.info()      
    logger.info(df_desc)
    nulls = df[df.nbhd_id != "NSA"].isnull().sum(axis=0)
    nsa_events = df[df.nbhd_id == "NSA"]
    
    def test_nulls(self):
        assert self.nulls[
            ["nbhd_id", "neighbourhood", 
            "crime_type", "sq_metres", "population"]
        ].sum() == 0, "you have nulls in crital cols"
        assert self.nulls[
            ["occurrencedayofweek", "premisetype", 
            "occurrenceyear", "occurrencedayofweek"]
        ].max() / self.df.shape[0] < .01, "you have more nulls than expected in important cols"
    
    def test_join_coverage(self):
        assert self.nulls[["nbhd_id", "nbhd_nbhd_id"]].max() == 0, "nulls in join keys"

    def test_pk_uniqueness(self):
        assert (
            self.df[["event_unique_id", "crime_type"]].drop_duplicates().shape[0]
            ==
            self.df.shape[0]
        ), "pk is not unique"

    def test_crimes_counts(self):
        counts = self.df.crime_type.value_counts()
        assert counts.max() / counts.sum() < .7
        assert counts.index[counts.argmax()] == "Assault"
        
    def test_crimes_per_year(self):
        crimes_per_year = (self.df
            .groupby(["crime_type", "occurrenceyear"])
            ["event_unique_id"]
            .count()
            .reset_index()
            .rename(columns={"event_unique_id": "n"})
            .sort_values(by=["crime_type", "n"], ascending=False)
        )
        crimes_per_year.to_csv("./reports/crimes_per_year.csv")  
        self.logger.info(crimes_per_year)
        yearly_stats_per_crime = (
            crimes_per_year
            .groupby("crime_type")["n"]
            .agg(["mean", "std", "max", "min", len])
        )
        yearly_stats_per_crime["max_minus_min_year_per_crime"] = (
            yearly_stats_per_crime["max"] - yearly_stats_per_crime["min"]
        )
        self.logger.info(yearly_stats_per_crime)
        assert (yearly_stats_per_crime["max_minus_min_year_per_crime"]).max() < 4000

    def test_crimes_by_premise(self):
        crimes_per_premise = (self.df
            .groupby(["crime_type", "premisetype"])
            ["event_unique_id"]
            .count()
            .reset_index()
            .rename(columns={"event_unique_id": "n"})
            .sort_values(by=["crime_type", "n"], ascending=False)
        )
        crimes_per_premise.to_csv("./reports/crimes_per_premise.csv")  
        self.logger.info(crimes_per_premise)
        crimes_per_premise.sort_values(by=["premisetype", "n"], ascending=False, inplace=True)
        self.logger.info(crimes_per_premise)
        assert crimes_per_premise.iloc[0]["crime_type"] == "Assault", "most common outside crime not assault"

    def test_nsa_events(self):
        self.assertLess(
            self.nsa_events.shape[0] / self.df.shape[0] * 100,
            2, "nsa events are more than 2% of all crimes"
        )

if __name__ == "__main__":
    unittest.main()
