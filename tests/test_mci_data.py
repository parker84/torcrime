import unittest
from src.models.averaging_model import AvgModel
import pandas as pd
from sqlalchemy import create_engine
from decouple import config
from src.utils.logger import init_logger
engine = create_engine(config('ENGINE_PATH'))
conn = engine.connect()


class TestMCIData(unittest.TestCase):

    df = pd.read_sql(
            "select * from src.mci_data", 
            con=conn)
    logger = init_logger("TestMCIData")  
    df_desc = df.describe()
    df.info()      
    logger.info(df_desc)
    nulls = df.isnull().sum(axis=0)
    chosen_cols = ["event_unique_id", "Hood_ID", "MCI", "offence", "premises_type", 
                    "Neighbourhood", "occurrencedayofweek", "occurrencehour", 
                    "occurrencedate", "occurrenceyear"]

    def test_duplicates(self):
        assert (
            self.df[["event_unique_id"]].drop_duplicates().shape[0]
            / self.df.shape[0]
        ) > .8, "too many duplicate rows of ids"
        unique_event_ids = self.df[["event_unique_id"]].drop_duplicates().shape[0]
        filtered_cols = ["event_unique_id"]
        last_unq_rows = unique_event_ids
        for col in self.chosen_cols:
            filtered_cols.append(col)
            unq_rows = self.df[filtered_cols].drop_duplicates().shape[0]
            self.logger.info(f"unq rows: {unq_rows}, w cols: {filtered_cols}")
            last_unq_rows = unq_rows
        assert (
            self.df[self.chosen_cols].drop_duplicates().shape[0]
            == 
            self.df[[ 'event_unique_id', 'Hood_ID', 'MCI', 'offence']].drop_duplicates().shape[0]
        ), "dups in unexpected cols"
        assert (
            self.df[[ 'event_unique_id', 'Hood_ID', 'MCI']].drop_duplicates().shape[0]
            /
            self.df[[ 'event_unique_id', 'Hood_ID', 'MCI', 'offence']].drop_duplicates().shape[0]
        ) > .9, "offence duplicated more than expecctedd for the same MCI"
        assert (
            self.df[[ 'event_unique_id', 'Hood_ID']].drop_duplicates().shape[0]
            /
            self.df[['event_unique_id', 'Hood_ID', 'MCI']].drop_duplicates().shape[0]
        ) > .9, "MCI duplicated more than expecctedd for the same event"
        assert (
            self.df[['event_unique_id', 'Hood_ID', 'Neighbourhood']].drop_duplicates().shape[0]
            ==
            self.df[['event_unique_id']].drop_duplicates().shape[0]
        ), "dup hoods for same event"

    def test_nulls(self):
        assert self.df[self.chosen_cols].isnull().sum().max() < 100, "have more nulls than expected"  
        assert self.df[
            [col for col in self.chosen_cols if col != "occurrencedayofweek" and col != "occurrenceyear"]
        ].isnull().sum().max() == 0, "have nulls"  

if __name__ == "__main__":
    unittest.main()
