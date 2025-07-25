from newsapi import NewsApiClient
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from time import time

load_dotenv()
api = os.environ.get("NEWS_API")
CACHE_FILE = "cached_news.json"
DATE_FILE = "current_date.txt"
newsapi = NewsApiClient(api_key=api)

CACHE_FILE2 = "news_cache.json"
CACHE_TIMEOUT = 300  # 5 minutes


# Load cache from file if exists
def load_cache():
    if os.path.exists(CACHE_FILE2):
        with open(CACHE_FILE2, "r") as f:
            return json.load(f)
    return {}


# Save cache to file
def save_cache(cache):
    with open(CACHE_FILE2, "w") as f:
        json.dump(cache, f)


def get_all_news(query):
    cache = load_cache()
    now = time()

    # Check if query exists and is not expired
    if query in cache:
        entry = cache[query]
        if now - entry["timestamp"] < CACHE_TIMEOUT:
            return entry["articles"]

    # Fetch new data
    all_articles = newsapi.get_everything(
        q=query,
        language="en",
        sort_by="relevancy",
        page_size=10,
    )

    # Save to cache
    cache[query] = {
        "timestamp": now,
        "articles": all_articles,
    }
    save_cache(cache)

    return all_articles


def get_today_news():
    current_date = datetime.today().strftime("%Y-%m-%d")

    # If date mismatch or no files → fetch and save
    if not os.path.exists(DATE_FILE) or open(DATE_FILE).read() != current_date:
        all_articles = newsapi.get_everything(
            q="india",
            language="en",
            sort_by="relevancy",
            page_size=10,
        )
        # Save to cache
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(all_articles, f, indent=2)

        with open(DATE_FILE, "w") as f:
            f.write(current_date)

        return all_articles

    # Else, load cached news
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
