
from decouple import config
import shopify
import pandas as pd
import json
from geopy.geocoders import Nominatim

class BuildUserDf():

    def __init__(self):
        self.geolocator = Nominatim(user_agent="toronto_crime_app")
        shopify.ShopifyResource.set_site(config("SHOP_URL"))
    
    def get_and_set_customer_df(self):
        customers = shopify.Customer.search()
        self.customer_df = pd.DataFrame([
            json.loads(customer.to_json().decode("utf-8").replace("'", '"'))["customer"]
            for customer in customers
        ])
    
    def set_customer_df(self, customer_df):
        self.customer_df = customer_df

    def build_user_df(self):
        assert self.customer_df is not None, "you need to set your customer_df first"
        user_df = self._filter_to_paying_customer()
        user_df = self._add_lat_lon_to_df(user_df)  
        user_df = self._add_km_radius_for_30m_walking(user_df) 
        return user_df 

    def _filter_to_paying_customer(self):
        # TODO: better handle users cancelling
        user_df = self.customer_df.dropna(axis=0, subset=["default_address"])[
            self.customer_df.verified_email
        ][self.customer_df.orders_count > 0][
            self.customer_df.state == "enabled"
        ]
        user_df = user_df[user_df.total_spent.astype(float) > 0]
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
    
    def _add_km_radius_for_30m_walking(self, df):
        hours = .5
        km_radius = round(hours * 5, 3) # we assume 5 km/h walk speed
        df["km_radius"] = km_radius
        return df

