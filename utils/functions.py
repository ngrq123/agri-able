import requests

def reverse_geocode(lat_lon):
    """
    Calls the Nominatim API to conduct reverse geocoding.
    See https://nominatim.org/release-docs/develop/api/Reverse/ for more.
    :param lat_lon: tuple of latitude and longitude of selected location
    :return: response: response in json format.
    """
    URL = 'https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat={lat}&lon={lon}'
    r = requests.get(URL.format(lat=lat_lon[0],lon=lat_lon[1]))
    response = r.json()

    return response