import os
import json
import requests
import requests_cache
from retry_requests import retry
import openmeteo_requests
from datetime import datetime
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


def fetch_weather(location, day):
    assert 1 <= day <= 3, "Day must be 1, 2, or 3"

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto",
    }

    response = requests.get(url, params=params)
    data = response.json()
    daily = data["daily"]
    i = day - 1

    return {
        "city": location["city"],
        "region": location["region"],
        "date": daily["time"][i],
        "temperature": daily["temperature_2m_max"][i],
        "min_temp": daily["temperature_2m_min"][i],
        "precipitation": daily["precipitation_sum"][i],
    }


def get_weather_data(day):
    update_location_if_needed()
    location = get_location()
    return fetch_weather(location, day)


# Optional CLI execution
if __name__ == "__main__":
    weather = get_weather_data(2)
    print(json.dumps(weather, indent=2))
