
from decouple import config
import shopify
import pandas as pd
import json
from geopy.geocoders import Nominatim

class BuildUserDf():

    def __init__(self):
        shopify.ShopifyResource.set_site(config("SHOP_URL"))
        customers = shopify.Customer.search()
        self.customer_df = pd.DataFrame([
            json.loads(customer.to_json().decode("utf-8").replace("'", '"'))["customer"]
            for customer in customers
        ])
        self.geolocator = Nominatim(user_agent="toronto_crime_app")
    
    def build_user_df(self):
        user_df = self._filter_to_paying_customer()
        user_df = self._add_lat_lon_to_df(user_df)   
        return user_df 

    def _filter_to_paying_customer(self):
        user_df = self.customer_df.dropna(axis=0, subset=["default_address"])[
            self.customer_df.verified_email
        ][self.customer_df.orders_count > 0]
        return user_df
    
    def _add_lat_lon_to_df(self, df1):
        """[summary]

        Args:
            df (pd.DataFrame): including "default_address" column
        """
        df = df1.copy()
        df["tor_address"] = [
            f"{row.default_address['address1']}, Toronto"
            for ix, row in df.iterrows()
        ]
        locs = [
            self.geolocator.geocode(address)
            for address in df["tor_address"]
        ]
        df["lat"] = [
            loc.latitude for loc in locs
        ]
        df["lon"] = [
            loc.longitude for loc in locs
        ]
        return df

