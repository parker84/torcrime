from dlearn.utils.base import BaseHelpers

class Predict(BaseHelpers):

    def __init__(self, df, model, **kwargs):
        """[summary]

        Arguments:
            df {[type]} -- needs to have the following columns:
                            ["premisetype", "nbhd_id", "neighbourhood",
                                "sq_metres", "crime_type", "occurrenceyear"]
            model {function} -- w predict function that outputs a df 
                                    including the following columns:
                                        ["nbhd_id", "expected_crimes_per_day"]
        """
        super(Predict, self).__init__(**kwargs)
        self.df = df
        self.model = model
        self.check_df()
    
    def check_df(self):
        for col in ["premisetype", "nbhd_id", "neighbourhood",
                    "sq_metres", "crime_type", "occurrenceyear"]:
            assert col in self.df.columns, f"{col}"

    def filter_df(self, premises, crimes, max_year, min_year):
        """filter down the df for the viz

        Arguments:
            premises {list} -- [description]
            crimes {list} -- [description]
            max_year {int} -- max_year inclusive
            min_year {int} -- min_year inclusive
        """
        self.log.info(f"shape before filtering: {self.df.shape}")
        self.df_filtered = self.df[
            self.df.premisetype.isin(premises) & 
            self.df.crime_type.isin(crimes) & 
            self.df.occurrenceyear <= max_year 
        ]
        self.df_filtered = self.df_filtered[
            self.df_filtered.occurrenceyear >= min_year
        ]
        self.days_of_potential_crime = 365 * (max_year - min_year + 1)
        self.log.info(f"shape after filtering: {self.df.shape}")

    def get_predicted_cases_per_nbhd_per_day(self):
        assert self.days_of_potential_crime is not None, "filter df first"
        cases_per_nbhd = self.model.predict(
            self.df_filtered, self.days_of_potential_crime
        )
        assert "expected_crimes_per_day" in cases_per_nbhd.columns, \
            "missing required column from predict function on model"
        return cases_per_nbhd

    def predict_cases_per_sq_km_per_nbhd_per_day(self):
        cases_per_nbhd = self.get_predicted_cases_per_nbhd_per_day()
        cases_w_sq_metres = cases_per_nbhd.merge(
            self.df_filtered[["nbhd_id", "sq_metres", "neighbourhood"]].drop_duplicates(),
            on=["nbhd_id"], how="left"
        )
        assert cases_w_sq_metres.shape[0] == cases_per_nbhd.shape[0], "join is off"
        cases_w_sq_metres["expected_crimes_per_day_per_sq_km"] = (
            cases_w_sq_metres.expected_crimes_per_day
            / (cases_w_sq_metres.sq_metres * 1e-6)
        )
        self.log.info("\n" + str(cases_w_sq_metres.describe()))
        return cases_w_sq_metres