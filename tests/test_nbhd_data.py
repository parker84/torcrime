import unittest
from src.models.averaging_model import AvgModel
import pandas as pd
from sqlalchemy import create_engine
from decouple import config
from src.utils.logger import init_logger
engine = create_engine(config('ENGINE_PATH'))
conn = engine.connect()


class TestNbhdData(unittest.TestCase):

    df = pd.read_sql(
            "select * from stg.nbhd_data", 
            con=conn)
    logger = init_logger("TestNbhdData")  
    df_desc = df.describe()
    df.info()      
    logger.info(df_desc)
    nulls = df.isnull().sum(axis=0)

    def test_nulls(self):
        assert self.nulls.max() == 0, "you have nulls"
    
    def test_shape_area_equals_sq_metres(self):
        """
        resources:
        - https://en.wikipedia.org/wiki/Demographics_of_Toronto_neighbourhoods
        - https://www.google.com/search?q=how+many+square+km+is+toronto&rlz=1C5GCEA_enCA890CA890&oq=how+many+square+km+is+to&aqs=chrome.1.69i57j0l7.8271j1j7&sourceid=chrome&ie=UTF-8
        """
        total_sq_metres = self.df.sq_metres.sum()
        total_sq_kms = 1e-6 * total_sq_metres
        assert total_sq_kms < 650 and total_sq_kms > 620, "total sq kms for toronto not in reasonable range"
        alderwood_sq_kms = 1e-6 * self.df[self.df.neighbourhood == "Alderwood"].sq_metres.iloc[0]
        assert alderwood_sq_kms < 5.5 and total_sq_kms > 4.5, "total sq kms for alderwood not in reasonable range"

    def test_population(self):
        assert self.df.population.sum() > 2e+06 and self.df.population.sum() < 3e+06, "population wrong"


if __name__ == "__main__":
    unittest.main()
