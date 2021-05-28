
from decouple import config
import shopify
import pandas as pd
import json
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

class BuildUserDf():

    def __init__(self):
        geolocator = Nominatim(user_agent="toronto_crime_app")
        self.geocoder = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        shopify.ShopifyResource.set_site(config("SHOP_URL"))
    
    def get_and_set_customer_df(self):
        customers = shopify.Customer.search()
        self.customer_df = pd.DataFrame([
            json.loads(customer.to_json().decode("utf-8").replace("'", '"'))["customer"]
            for customer in customers
        ])
    
    def _set_customer_df(self, customer_df):
        self.customer_df = customer_df

    def _set_order_df(self, order_df):
        self.order_df = order_df
        self.alert_order_df = (
            self.order_df[self.order_df["product_id"] == 6559870451734]
            .drop_duplicates(subset=["customer_id"])
        )

    def build_user_df(self):
        assert self.customer_df is not None, "you need to set your customer_df first"
        assert self.order_df is not None, "you need to set your order_df first"
        user_df = self._filter_to_alert_subscribers()
        user_df = self._add_lat_lon_to_df(user_df)  
        user_df = self._add_km_radius_for_30m_walking(user_df) 
        return user_df 

    def get_and_set_order_df(self):
        num_orders = shopify.Order.count()
        if num_orders <= 250:
            orders = shopify.Order.find(limit=250, status="any")
        else:
            orders = []
            # TODO: test this further for when we have more than 250 orders
            for i in range(num_orders % 250):
                orders_page = shopify.Order.find(limit=250, page=i+1, status="any")
                orders = orders.extend(orders_page)
        line_items = []
        for order in orders:
            order_dict = json.loads(order.to_json().decode("utf-8").replace("'", '"'))
            lines_per_order = order_dict["order"]["line_items"]
            # print(json.dumps(order_dict, indent=4))
            for line in lines_per_order:
                line["customer_id"] = order_dict["order"]["customer"]["id"]
            line_items.extend(lines_per_order)
        self._set_order_df(pd.DataFrame(line_items))
        

    def _filter_to_alert_subscribers(self):
        user_df = self.customer_df.dropna(axis=0, subset=["default_address"])[
            self.customer_df.verified_email
        ][self.customer_df.orders_count > 0][
            self.customer_df.state == "enabled"
        ].merge(self.alert_order_df, how="inner", left_on="id", right_on="customer_id")
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
            self.geocoder(address)
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

