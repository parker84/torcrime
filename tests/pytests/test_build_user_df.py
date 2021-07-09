import pytest
from src.utils.build_user_df import BuildUserDf
import pandas as pd
import numpy as np

@pytest.fixture
def mock_user_df():
    """Returns a user_df w 1 correct user and the rest that shouldn't be recieving emails

    Returns:
        [type]: [description]
    """
    default_address = {'id': 6319809265686, 'customer_id': 5126812467222, 'first_name': 'Brydon', 'last_name': 'Parker', 'company': '', 'address1': '12 Charlotte St', 'address2': 'Unit 501', 'city': 'Toronto', 'province': 'Ontario', 'country': 'Canada', 'zip': 'M5V 0M6', 'phone': '', 'name': 'Brydon Barker', 'province_code': 'ON', 'country_code': 'CA', 'country_name': 'Canada', 'default': False}
    customer_df = pd.DataFrame({
        "email": [
            "test_correct_everything@gmail.com", 
            "has_not_paid@gmail.com", 
            "has_no_address@gmail.com", 
            "has_not_verified_email@gmail.com", 
            "has_no_orders@gmail.com", 
            "state_not_enabled@gmail.com",
            "has_no_spend@gmail.com", 
        ],
        "id": [1,2,3,4,5,6,7],
        "default_address": [
            default_address,
            default_address,
            np.nan,
            default_address,
            default_address,
            default_address,
            default_address
        ],
        "verified_email": [True, True, True, False, True, True, True],
        "total_spent": [1, 0, 1, 1, 1, 1, 0],
        "orders_count": [1, 0, 1, 1, 0, 1, 1],
        "state": ["enabled", "enabled", "enabled", "enabled", "enabled", "not_enabled", "enabled"]
    })
    order_df = pd.DataFrame({
        "customer_id": [1, 3, 4, 6],
        "product_id": [6559870451734] * 4
    })
    builder = BuildUserDf()
    builder._set_customer_df(customer_df)
    builder._set_order_df(order_df)
    user_df = builder.build_user_df()
    return user_df

@pytest.fixture
def real_user_df() -> pd.DataFrame:
    """Returns our actual user_df
    """
    builder = BuildUserDf()
    builder.get_and_set_customer_df()
    builder.get_and_set_order_df()
    user_df = builder.build_user_df()
    return user_df


def test_user_filtering(mock_user_df):
    assert mock_user_df.shape[0] == 3, "you should only have 1 user that made it through the filters"

def test_address_extraction(mock_user_df):
    assert mock_user_df.iloc[0]["tor_address"] == '12 Charlotte St, Toronto'

def test_getting_customer_info():
    builder = BuildUserDf()
    builder.get_and_set_customer_df()
    builder.get_and_set_order_df()
    mock_user_df = builder.build_user_df()
    assert builder.customer_df.shape[0] > 0, "not extracting any customers from the shopify api"
    if builder.customer_df.total_spent.sum() == 0:
        assert mock_user_df.shape[0] == 0, "you have rows in your user df even though no one has spent anything"

def test_km_radius(mock_user_df):
    assert mock_user_df.iloc[0].km_radius == 2.5, "km_radius is not correct"

def test_all_real_users_have_lat_lon(real_user_df):
    assert sum(real_user_df.lat == 'Could Not Geocode Address') == 0, 'You have addresses from users you could not geocode'
