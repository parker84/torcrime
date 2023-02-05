import pandas as pd
from sqlalchemy import create_engine
from decouple import config
from datetime import datetime
from src.utils.geocoder import GeoCoder


class Users():
    
    def __init__(self):
        self.geocoder = GeoCoder()
        self.user_table = 'users'
        self.engine = create_engine(config('DATABASE_URL'))
        self.conn = self.engine.connect()

    def create_user(self, email, address):
        new_user_df = pd.DataFrame([])
        new_user_df['email'] = [email]
        new_user_df['address'] = [address]
        new_user_df['created_at'] = [str(datetime.now())]
        new_user_df.to_sql(self.user_table, con=self.conn, if_exists='append', schema=config('DB_PROD_SCHEMA'))
    
    def get_users(self):
        user_df = pd.read_sql(f"select * from {config('DB_PROD_SCHEMA')}.{self.user_table}", con=self.conn)
        user_df = self._add_lat_lon_to_df(user_df)
        user_df = self._add_km_radius_for_30m_walking(user_df)
        return user_df

    def _add_lat_lon_to_df(self, df1):
        """[summary]

        Args:
            df (pd.DataFrame): including "address" column
        """
        df = df1.copy()
        df["tor_address"] = [
            f"{row['address'].split(',')[0]}, Toronto"
            for ix, row in df.iterrows()
        ]
        locs = [
            self.geocoder.geocode(address)
            for address in df["tor_address"]
        ]
        if sum([loc == 'Could Not Geocode Address' for loc in locs]) > 0:
            logger.error('You have addresses from users you could not geocode')
        df["lat"] = [
            loc.latitude if loc != 'Could Not Geocode Address' 
            else loc
            for loc in locs
        ]
        df["lon"] = [
            loc.longitude if loc != 'Could Not Geocode Address' 
            else loc
            for loc in locs
        ]
        return df
    
    def _add_km_radius_for_30m_walking(self, df):
        hours = .5
        km_radius = round(hours * 5, 3) # we assume 5 km/h walk speed
        df["km_radius"] = km_radius
        return df
