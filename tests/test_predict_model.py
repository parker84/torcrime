import unittest
from src.models.predict_model import Predict
from src.models.averaging_model import AvgModel
import pandas as pd
import numpy as np

class TestPredict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        model = AvgModel()
        cls.df = pd.DataFrame(
            [
                ["Outdoor", "Annex", 4e+6, "Assualt", 2019],
                ["Outdoor", "Annex", 4e+6, "Assualt", 2018],
                ["Outdoor", "Annex", 4e+6, "Murder", 2019],
                ["Outdoor", "Annex", 4e+6, "Assualt", 2019],
                ["Outdoor", "Annex", 4e+6, "Assualt", 2017],
                ["Outdoor", "Annex", 4e+6, "Assualt", 2019],
                ["Indoor", "Annex", 4e+6, "Assualt", 2019],
                ["Indoor", "High Park", 4e+6, "Assualt", 2019],
                ["Outdoor", "High Park", 4e+6, "Assualt", 2019],
                ["Indoor", "High Park", 4e+6, "Robbery", 2019],
                ["Indoor", "High Park", 4e+6, "Assualt", 2019],
            ], 
            columns=["premisetype", "neighbourhood", 
                    "sq_metres", "crime_type", "occurrenceyear"]
        )
        cls.predicter = Predict(cls.df, model)
    
    def test_preds_no_filter(self):
        self.predicter.filter_df(
            ["Outdoor", "Indoor"],
            ["Robbery", "Assualt", "Murder"],
            2019, 2017
        )
        preds = self.predicter.get_predicted_cases_per_nbhd_per_day()
        assert preds.crimes_counts_per_nbhd.tolist() == [7,4]
        assert (
            preds.expected_crimes_per_hour.round(3).tolist()
            == 
            (np.array([7,4]) / (365*3)).round(3).tolist()
        )
        preds_per_metre = self.predicter.predict_cases_per_sq_km_per_nbhd_per_hour()
        assert (
            preds_per_metre.expected_crimes_per_hour_per_sq_km.round(3).tolist()
            == 
            (np.array([7,4]) / (365*3*4)).round(3).tolist()
        )


if __name__ == "__main__":
    unittest.main()