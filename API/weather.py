import os
import json
import requests
import requests_cache
import openmeteo_requests
from datetime import datetime
from retry_requests import retry
import unicodedata

# Constants
CACHE_DIR = ".cache"
DATE_FILE = "current_date.txt"
IP_INFO_FILE = "ip_details.json"


def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        response.raise_for_status()
        return response.json()["ip"]
    except Exception as e:
        raise RuntimeError("Failed to get public IP") from e


def fetch_location(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=216"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "city": unicodedata.normalize("NFD", data["city"])
            .encode("ascii", "ignore")
            .decode("ascii"),
            "region": data["regionName"],
            "latitude": data["lat"],
            "longitude": data["lon"],
        }
    except Exception as e:
        raise RuntimeError("Failed to fetch location") from e


def update_location_if_needed():
    current_date = datetime.today().strftime("%Y-%m-%d")
    if not os.path.exists(DATE_FILE) or open(DATE_FILE).read() != current_date:

        ip = get_public_ip()
        location = fetch_location(ip)
        with open(IP_INFO_FILE, "w") as f:
            json.dump(location, f)
        with open(DATE_FILE, "w") as f:
            f.write(current_date)


def get_location():
    if not os.path.exists(IP_INFO_FILE):
        update_location_if_needed()
    with open(IP_INFO_FILE, "r") as f:
        return json.load(f)


def fetch_weather(location):
    session = requests_cache.CachedSession(CACHE_DIR, expire_after=3600)
    retry_session = retry(session, retries=3, backoff_factor=0.3)
    client = openmeteo_requests.Client(session=retry_session)

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": [
            "temperature_2m",
            "precipitation",
            # "relative_humidity_2m",
            # "apparent_temperature",
            # "is_day",
            # "rain",
            # "showers",
        ],
        "timezone": "auto",
        "forecast_days": 1,
    }

    response = client.weather_api(
        "https://api.open-meteo.com/v1/forecast", params=params
    )[0]
    current = response.Current()
    date = datetime.today().strftime("%d %B %Y")

    return {
        "city": location["city"],
        "region": location["region"],
        "temperature": int(current.Variables(0).Value()),
        "date": date,
        "precipitation": current.Variables(1).Value(),
        # "humidity": current.Variables(1).Value(),
        # "feels_like": current.Variables(2).Value(),
        # "is_day": bool(current.Variables(3).Value()),
        # "rain": current.Variables(5).Value(),
        # "showers": current.Variables(6).Value(),
    }


def get_weather_data():
    update_location_if_needed()
    location = get_location()
    return fetch_weather(location)


# Optional CLI execution
if __name__ == "__main__":
    weather = get_weather_data()
    print(json.dumps(weather, indent=2))
