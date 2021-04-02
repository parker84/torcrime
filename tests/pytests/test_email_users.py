import pytest
from src.utils.email_users import EmailUsers
import pandas as pd

@pytest.fixture
def user_df():
    '''Returns a Wallet instance with a zero balance'''
    user_df = pd.DataFrame({
        "lat": [43.60, 50, 43.63], 
        "lon": [-79.35, -90, -79.55], 
        "km_radius": [3, 3, 3], 
        "email": ["toronto.crime123@gmail.com"] * 3
    })
    return user_df

def test_email_users(user_df):
    email_users = EmailUsers(user_df)
    sel_users = email_users.filter_to_users_near_the_event(43.60, -79.35)
    email_users.email_the_right_users(
        sel_users,
        "STABBING: Chestnut St + Dundas St W * 4:58 pm * - Reports of man stabbed - Reports it may have been a robbery - Sus… https://t.co/jfQLPRTNZ3", 
        "Stabbing"
    )
    assert sel_users.shape[0] == 1