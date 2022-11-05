import pytest
import logging
import coloredlogs
import os
from src.utils.users import Users


logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)

@pytest.fixture
def users():
    return Users()

@pytest.fixture
def user():
    return {
        'email': 'brydonparker4@gmail.com',
        'address': '1 Dundas St, Toronto'
    }

def test_add_user(users, user):
    users.create_user(user['email'], user['address'])
    user_df = users.get_users()
    assert user_df.shape[0] > 0
    assert sum(user_df['email'] == 'brydonparker4@gmail.com') > 0
    print(user_df.head())
    assert 'lat' in user_df.columns
