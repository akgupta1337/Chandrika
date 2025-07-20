from urllib.parse import urlparse, unquote
import wikipediaapi
import requests
import os
import json

from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("GAPI_KEY")
SEARCH_ENGINE_ID = os.environ.get("ENG_ID")
CACHE_DIR = "cache"

os.makedirs(CACHE_DIR, exist_ok=True)
wiki = wikipediaapi.Wikipedia(user_agent="123Robot@yahoo.com", language="en")


def search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query + " site:en.wikipedia.org",
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "lr": "lang_en",
        "num": 2,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        if "items" not in results:
            print("No search results found.")
            return []
        return results["items"]
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Google API request failed: {e}")
        return []


def extract_wikipedia_title(url):
    parsed = urlparse(url)
    if "wikipedia.org" not in parsed.netloc:
        return None
    parts = parsed.path.split("/wiki/")
    if len(parts) != 2:
        return None
    return unquote(parts[1])


def get_wikipedia_summary(title):
    if not title:
        return None
    page = wiki.page(title)
    if page.exists():
        return page.summary
    else:
        return None


def get_context(query):
    cache_path = os.path.join(
        CACHE_DIR, f"context_{query.lower().replace(' ', '_')}.json"
    )

    if os.path.exists(cache_path):
        print("found context for " + query)
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    items = search(query)
    summaries = []
    for item in items:
        url = item.get("link", "")
        title = extract_wikipedia_title(url)
        if not title:
            print(f"[SKIP] Not a valid Wikipedia URL: {url}")
            continue

        summary = get_wikipedia_summary(title)
        if summary:
            summaries.append(summary)
        else:
            print(f"[WARN] Wikipedia page not found or empty for: {title}")

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    return summaries


def search_images(query):
    cache_path = os.path.join(
        CACHE_DIR, f"images_{query.lower().replace(' ', '_')}.json"
    )

    if os.path.exists(cache_path):
        print("found image for " + query)
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "lr": "lang_en",
        "num": 3,
        "searchType": "image",
        "imgSize": "xxlarge",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()

        if "items" not in results:
            print("No image search results found.")
            return []

        image_links = [item.get("link") for item in results["items"] if "link" in item]

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(image_links, f, ensure_ascii=False, indent=2)

        return image_links

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Google API request failed: {e}")
        return []
