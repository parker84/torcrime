import pytest
from src.utils.build_user_df import BuildUserDf
import pandas as pd

@pytest.fixture
def user_df():
    '''Returns a Wallet instance with a zero balance'''
    builder = BuildUserDf()
    user_df = builder.build_user_df()
    return user_df

def test_email_users(user_df):
    assert user_df.shape[0] > 0