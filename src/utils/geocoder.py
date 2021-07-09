from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

STRINGS_TO_REPLACE = [
    ' st',
    ' st.',
    ' av',
    ' ave',
    ' rd',
    ' cres',
    ' blvd',
    ' dr'
    # long
    ' street',
    ' avenue',
    ' road',
    ' boulevard',
    ' crescent',
    ' drive'
    # direction
    ' n',
    ' w',
    ' e',
    ' s'
]

class GeoCoder():

    def __init__(self, geolocator) -> None:
        self.geocoder = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    def geocode(self, address):
        location = self.geocoder(address)
        if location is None:
            clean_address = self._clean_address(address)
            location = self.geocoder(clean_address)
            if location is None:
                location = "Could Not Geocode Address"
        return location


    def _clean_address(self, address):
        if '+' in address or ' and ' in address.lower() or '&' in address:
            return self._clean_intersection(address) + ', Canada'
        else:
            return address + ', Canada'
    
    def _clean_intersection(self, address):
        clean_address = address.lower()
        for str_ in STRINGS_TO_REPLACE:
            clean_address = clean_address.replace(str_ + ' ', ' ')
            clean_address = clean_address.replace(str_ + ',', ',')
        return clean_address
