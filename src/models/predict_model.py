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
                                        ["nbhd_id", "expected_crimes_per_hour"]
        """
        super(Predict, self).__init__(**kwargs)
        self.df = df
        self._get_nbhds()
        self.model = model
        self.check_df()

    def check_df(self):
        for col in ["premisetype", "nbhd_id", "neighbourhood",
                    "sq_metres", "crime_type", "occurrenceyear"]:
            assert col in self.df.columns, f"{col}"

    def filter_df(self, premises, crimes, max_year, 
                    min_year, min_hour, max_hour,
                    days_of_week):
        """filter down the df for the viz

        Arguments:
            premises {list} -- [description]
            crimes {list} -- [description]
            max_year {int} -- max_year inclusive
            min_year {int} -- min_year inclusive
        """
        self.log.info(f"shape before filtering: {self.df.shape}")
        self.df_filtered = self.df[
            self.df.premisetype.astype(str).isin(premises)
        ]
        self.log.info(f"rows after filtering from premise: {self.df_filtered.shape[0]}")
        self.df_filtered = self.df_filtered[
            self.df_filtered.occurrenceyear <= max_year
        ]
        self.log.info(f"rows after filtering from premise, max_year: {self.df_filtered.shape[0]}")
        self.df_filtered = self.df_filtered[
            self.df_filtered.crime_type.isin(crimes)
        ]
        self.log.info(f"rows after filtering from premise, max_year and crime: {self.df_filtered.shape[0]}")
        self.df_filtered = self.df_filtered[
            self.df_filtered.occurrencehour < max_hour
        ]
        self.log.info(f"rows after filtering from max hour: {self.df_filtered.shape[0]}")
        self.df_filtered = self.df_filtered[
            [str(day).strip() in days_of_week 
             for day in self.df_filtered.occurrencedayofweek.values]
        ]
        self.log.info(f"rows after filtering from max hour and dow: {self.df_filtered.shape[0]}")
        self.df_filtered = self.df_filtered[
            self.df_filtered.occurrenceyear >= min_year
        ]
        self.df_filtered = self.df_filtered[
            self.df_filtered.occurrencehour >= min_hour
        ]
        self.log.info(f"rows after filtering from premise, min hour and min year: {self.df_filtered.shape[0]}")
        self.hours_of_potential_crime = (
            365 * 
            (max_year - min_year + 1) * 
            (len(days_of_week) / 7) * 
            (max_hour - min_hour)
        )
        self.log.info(f"shape after filtering: {self.df_filtered.shape}")

    def get_predicted_cases_per_nbhd_per_hour(self):
        assert self.hours_of_potential_crime is not None, "filter df first"
        cases_per_nbhd = self.model.predict(
            self.df_filtered, self.hours_of_potential_crime
        )
        assert self.nbhd_df is not None, "need to run self._get_nbhds first"
        cases_for_all_nbhds = (
            self.nbhd_df
            .merge(cases_per_nbhd, on="nbhd_id", how="left")
            .fillna(0)
        )
        assert "expected_crimes_per_hour" in cases_for_all_nbhds.columns, \
            "missing required column from predict function on model"
        return cases_for_all_nbhds

    def predict_cases_per_sq_km_per_nbhd_per_hour(self):
        cases_per_nbhd = self.get_predicted_cases_per_nbhd_per_hour()
        cases_w_sq_metres = cases_per_nbhd.merge(
            self.df_filtered[["nbhd_id", "sq_metres", "neighbourhood"]].drop_duplicates(),
            on=["nbhd_id"], how="left"
        )
        assert cases_w_sq_metres.shape[0] == cases_per_nbhd.shape[0], "join is off"
        cases_w_sq_metres["expected_crimes_per_hour_per_sq_km"] = (
            cases_w_sq_metres.expected_crimes_per_hour
            / (cases_w_sq_metres.sq_metres * 1e-6)
        )
        self.log.info("\n" + str(cases_w_sq_metres.describe()))
        return cases_w_sq_metres

    def predict_cases_per_10k_people_per_nbhd_per_hour(self):
        cases_per_nbhd = self.get_predicted_cases_per_nbhd_per_hour()
        cases_w_pop = cases_per_nbhd.merge(
            self.df_filtered[["nbhd_id", "population", "neighbourhood"]].drop_duplicates(),
            on=["nbhd_id"], how="left"
        )
        assert cases_w_pop.shape[0] == cases_per_nbhd.shape[0], "join is off"
        cases_w_pop["expected_crimes_per_hour_per_10k_people"] = (
            cases_w_pop.expected_crimes_per_hour
            / (cases_w_pop.population / 10000)
        )
        self.log.info("\n" + str(cases_w_pop.describe()))
        return cases_w_pop

    def _get_nbhds(self):
        self.nbhd_df = self.df[["nbhd_id"]].drop_duplicates()
    