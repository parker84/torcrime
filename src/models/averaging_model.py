from dlearn.utils.base import BaseHelpers
import pandas as pd


class AvgModel(BaseHelpers):

    def predict(self, df, days_of_potential_crime, **kwargs):
        """[summary]

        Arguments:
            df {[type]} -- needs to have the follwing cols: 
                            ["nbhd_id"]
        """
        super(AvgModel, self).__init__(**kwargs)
        self._check_cols(df)
        totals_per_nbhd = self._get_totals_per_nbhd(df)
        totals_per_nbhd["expected_crimes_per_day"] = (
            totals_per_nbhd["crimes_counts_per_nbhd"] / 
            days_of_potential_crime
        )
        totals_per_nbhd["days_of_potential_crime"] = days_of_potential_crime
        return totals_per_nbhd

    def _check_cols(self, df):
        for col in ["nbhd_id"]:
            assert col in df.columns, f"{col} missing"

    def _get_totals_per_nbhd(self, df):
        totals_per_nbhd = df.nbhd_id.value_counts()
        return (
            pd.DataFrame(totals_per_nbhd)
            .reset_index()
            .rename(columns={
                "nbhd_id": "crimes_counts_per_nbhd",
                "index": "nbhd_id"
            })
        )