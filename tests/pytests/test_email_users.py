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
        "email": ["toronto.crime123@gmail.com"] * 3,
        "first_name": ["Jane"] * 3
    })
    return user_df

@pytest.fixture
def tweet_df():
    tweet_df = pd.DataFrame({
        "created_at": ["Sun Apr 04 19:34:55 +0000 2021", "Sun Apr 04 05:50:03 +0000 2021", "Fri Mar 26 14:04:08 +0000 2021"],
        "crime": ["Stabbing", "Shooting", "Person with a Knife"],
        "address": ["Chestnut St and Dundas St W, Toronto", "12 Charlotte St, Toronto", "Markham St and College St, Toronto"],
        "text": [
            "STABBING: Chestnut St + Dundas St W * 4:58 pm * - Reports of man stabbed - Reports it may have been a robbery - Sus… https://t.co/jfQLPRTNZ3",
            "SHOOTING: 12 Charlotte St * 4:58 pm * - Reports of man stabbed - Reports it may have been a robbery - Sus… https://t.co/jfQLPRTNZ3",
            "PERSON WITH A KNIFE: Markham St + College St - officers have checked the area, unable to locate male - officers are… https://t.co/XDV9uWCO45"
        ]
    })
    return tweet_df

def test_email_users(user_df, tweet_df):
    email_users = EmailUsers(user_df)
    sel_users = email_users.filter_to_users_near_the_event(43.60, -79.35)
    assert sel_users.shape[0] == 1, "should only be one user in the radius"
    for ix, row in tweet_df.iterrows():
        email_users.email_the_right_users(
            sel_users,
            row
        )