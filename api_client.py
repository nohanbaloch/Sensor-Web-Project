import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

NASA_API_KEY = os.getenv('NASA_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

def fetch_satellite_image(lat, lon):
    """Fetches satellite image URL from NASA Earth Assets API."""
    url = "https://api.nasa.gov/planetary/earth/assets"
    params = {
        'lon': lon,
        'lat': lat,
        'dim': 0.1,
        'api_key': NASA_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('url')
    except Exception as e:
        print(f"Error fetching satellite image: {e}")
    return None

def fetch_weather_data(lat, lon):
    """Fetches current weather data from OpenWeather API."""
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,
        'lon': lon,
        'appid': WEATHER_API_KEY,
        'units': 'metric'
    }
    try:
        response = requests.get(url, params=params)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def fetch_coordinates(location_name):
    """Fetches coordinates for a given location name."""
    url = "http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': location_name,
        'limit': 1,
        'appid': WEATHER_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200 and response.json():
            location_data = response.json()[0]
            return location_data.get('lat'), location_data.get('lon'), location_data.get('name')
    except Exception as e:
        print(f"Error fetching coordinates: {e}")
    return None, None, None

def fetch_location_name(lat, lon):
    """Reverse geocodes coordinates to find location name."""
    url = "http://api.openweathermap.org/geo/1.0/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'limit': 1,
        'appid': WEATHER_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200 and response.json():
            location_data = response.json()[0]
            # specific logic to get a readable name (e.g. London, GB)
            name = location_data.get('name')
            country = location_data.get('country')
            return f"{name}, {country}" if country else name
    except Exception as e:
        print(f"Error fetching location name: {e}")
    return None
