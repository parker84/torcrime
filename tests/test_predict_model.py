import unittest
from src.models.predict_model import Predict
from src.models.averaging_model import AvgModel
import pandas as pd
import numpy as np

DAYS_OF_WEEK = [
    "Monday", "Tuesday", "Wednesday", "Thursday", 
    "Friday", "Saturday", "Sunday"
]

class TestPredict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        model = AvgModel()
        cls.df = pd.DataFrame(
            [
                ["Outdoor", "Annex", 1, 4e+6, "Assualt", 2019, 1, "Saturday"],
                ["Outdoor", "Annex", 1, 4e+6, "Assualt", 2018, 1, "Saturday"],
                ["Outdoor", "Annex", 1, 4e+6, "Murder", 2019, 1, "Saturday"],
                ["Outdoor", "Annex", 1, 4e+6, "Assualt", 2019, 1, "Saturday"],
                ["Outdoor", "Annex", 1, 4e+6, "Assualt", 2017, 1, "Friday"],
                ["Outdoor", "Annex", 1, 4e+6, "Assualt", 2019, 2, "Saturday"],
                ["Indoor", "Annex", 1, 4e+6, "Assualt", 2019, 3, "Saturday"],
                ["Indoor", "High Park", 2, 4e+6, "Assualt", 2019, 1, "Saturday"],
                ["Outdoor", "High Park", 2, 4e+6, "Assualt", 2019, 1, "Saturday"],
                ["Indoor", "High Park", 2, 4e+6, "Robbery", 2019, 10, "Saturday"],
                ["Indoor", "High Park", 2, 4e+6, "Assualt", 2019, 1, "Monday"],
            ], 
            columns=["premisetype", "neighbourhood", "nbhd_id",
                    "sq_metres", "crime_type", "occurrenceyear",
                    "occurrencehour", "occurrencedayofweek"]
        )
        cls.predicter = Predict(cls.df, model)
    
    def test_preds_no_filter(self):
        self.predicter.filter_df(
            premises=["Outdoor", "Indoor"], 
            crimes=["Robbery", "Assualt", "Murder"], 
            max_year=2019, 
            min_year=2017, 
            min_hour=0,
            max_hour=24,
            days_of_week=DAYS_OF_WEEK
        )
        preds = self.predicter.get_predicted_cases_per_nbhd_per_hour()
        assert preds.crimes_counts_per_nbhd.tolist() == [7,4]
        assert (
            preds.expected_crimes_per_hour.round(3).tolist()
            == 
            (np.array([7,4]) / (365*3*24)).round(3).tolist()
        )
        preds_per_km = self.predicter.predict_cases_per_sq_km_per_nbhd_per_hour()
        self.assertEqual(
            preds_per_km["Probability of Crime"].round(2).tolist(),
            (100 * (np.array([7,4]) / (365*3*4*24))).round(2).tolist()
        )
        crime_counts = self.predicter.get_num_crimes()
        self.assertEqual(
            crime_counts["Number of Crimes"].round(2).tolist(),
            [7, 4]
        )

    def test_filtering(self):
        self.predicter.filter_df(
            premises=["Outdoor", "Indoor"], 
            crimes=["Robbery", "Assualt", "Murder"], 
            max_year=2019, 
            min_year=2017, 
            min_hour=0,
            max_hour=3,
            days_of_week=["Saturday", "Friday"]
        )
        preds = self.predicter.get_predicted_cases_per_nbhd_per_hour()
        assert preds.crimes_counts_per_nbhd.tolist() == [6,2]
        self.assertEqual(
            preds.expected_crimes_per_hour.round(3).tolist(),
            (np.array([6,2]) / (365*3*4*(2/7))).round(3).tolist()
        )
        preds_per_km = self.predicter.predict_cases_per_sq_km_per_nbhd_per_hour()
        self.assertEqual(
            preds_per_km["Probability of Crime"].round(3).tolist(),
            (100 * np.array([6,2]) / (365*3*4*4*(2/7))).round(3).tolist()
        )
        crime_counts = self.predicter.get_num_crimes()
        self.assertEqual(
            crime_counts["Number of Crimes"].round(2).tolist(),
            [6, 2]
        )


if __name__ == "__main__":
    unittest.main()