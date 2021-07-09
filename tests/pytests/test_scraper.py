import pytest
import logging
import coloredlogs
import os
from src.data.tweet_scrapper import TweetScrapper

logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)

@pytest.fixture
def tweet_scrapper():
    return TweetScrapper()

@pytest.fixture
def dict_tweet_scrappable():
    return {
        "text": "COLLISION: UPDATE\nEglinton Av E + McCowan Rd\n@TrafficServices is o/s investigating\n- man has been pronounced deceas… https://t.co/LGAQTCudE2"
    }

@pytest.fixture
def dict_tweet_unscrappable():
    return {
        "text": "MISSING:\nCromwell Collins, 78\n- last seen on Wed, July 7, at 2:30am in the Don Valley Pkwy + Eglinton Av E area… https://t.co/6JHPxoKUPj"
    }

def test_scrappable(tweet_scrapper, dict_tweet_scrappable):
    dict_tweet = tweet_scrapper._extract_entities_from_ops_tweet(dict_tweet_scrappable)
    assert round(dict_tweet['lat']) == 44, "latitude not properly extracted"
    assert dict_tweet['crime'] == 'collision', "crime not properly extracted"

def test_unscrappable(tweet_scrapper, dict_tweet_unscrappable):
    dict_tweet = tweet_scrapper._extract_entities_from_ops_tweet(dict_tweet_unscrappable)
    assert dict_tweet['lat'] == 'null', "latitude not properly extracted"
    assert dict_tweet['crime'] == 'missing', "crime not properly extracted"

