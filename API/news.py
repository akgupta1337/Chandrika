from newsapi import NewsApiClient
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()
api = os.environ.get("NEWS_API")
CACHE_FILE = "cached_news.json"
DATE_FILE = "current_date.txt"
newsapi = NewsApiClient(api_key=api)


def get_all_news(query):
    # Fetch articles
    all_articles = newsapi.get_everything(
        q=query,
        language="en",
        sort_by="relevancy",
        page_size=10,
    )

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
