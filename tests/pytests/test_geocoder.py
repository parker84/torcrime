import pytest
from src.utils.geocoder import GeoCoder
import logging
import coloredlogs
import os

logger = logging.getLogger(__name__)
coloredlogs.install(level=os.getenv("LOG_LEVEL", "INFO"), logger=logger)

@pytest.fixture
def geocoder():
    return GeoCoder()

@pytest.fixture
def intersections():
    return [
        #--------works without cleaning
        'Eglinton Ave W and Scarlett Rd, Toronto',
        'Kipling Ave and Rexdale Blvd, Toronto',
        #---------worked before, working now after cleaning:
        'Eglinton Av E + McCowan Rd, Toronto',
        'Oakwood Ave and Lanark Ave, Toronto',
        'Birchmount Rd and Bertrand Ave, Toronto',
        'Spadina Rd and Bloor Ave W, Toronto',
        'Bathurst St and Bainbridge Ave, Toronto'
        #---------work only w google maps
        'Lloyd Manor Rd and Eglington Ave W, Toronto',
        'Lake Shore Blvd W and Forty Second St, Toronto',
        'Lake Shore Blvd W + Forty Second St, Toronto'
    ]

@pytest.fixture
def non_intersections():
    return [
        '121 Eglinton Av E, Toronto',
        '12 Lloyd Manor Rd, Toronto',
        '124 Lake Shore Blvd W, Toronto'
    ]

@pytest.fixture
def non_addresses():
    return [
        'Not an address, Toronto',
    ]


def test_intersections(geocoder, intersections):
    for address in intersections:
        location = geocoder.geocode(address)
        assert location.latitude is not None, f"couldn't geocode: {address}"
        logger.debug(location)
        
def tests_non_intersections(geocoder, non_intersections):
    for address in non_intersections:
        location = geocoder.geocode(address)
        assert location.latitude is not None, f"couldn't geocode: {address}"

def test_cant_extract_address(geocoder, non_addresses):
    for address in non_addresses:
        location = geocoder.geocode(address)
        assert location == "Could Not Geocode Address"