from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="gpx-generator")
location = geolocator.geocode("Paris")
print(location.latitude, location.longitude)
