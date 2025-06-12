import requests
from django.conf import settings
from datetime import datetime, timezone


def fetch_newsdata_world_news():
    """
    Fetches general world news headlines from NewsData.io API.

    Returns:
        list: A list of dictionaries containing article details.
    """
    try:
        url = getattr(settings, 'NEWSDATA_WORLD_NEWS_URL', None)
        if not url:
            raise ValueError(
                "NEWSDATA_WORLD_NEWS_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        crumbs = []
        for article in data.get("results", []):
            title = article.get("title")
            url = article.get("link")
            summary = article.get("description")
            source = article.get("source_id")
            published_at_str = article.get("pubDate")

            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source if source else "NewsData.io World News",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"NewsData.io World News fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for NewsData.io World News: {val_err}")
        return []
    except Exception as e:
        print(f"NewsData.io World News unexpected error: {e}")
        return []


def fetch_newsapi_world_news():
    """
    Fetches general world news headlines from NewsAPI.org API (UK focus).

    Returns:
        list: A list of dictionaries containing article details.
    """
    try:
        url = getattr(settings, 'NEWS_API_URL', None)
        if not url:
            raise ValueError(
                "NEWS_API_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        crumbs = []
        # NewsAPI.org returns results under the 'articles' key
        for article in data.get("articles", []):
            title = article.get("title")
            url = article.get("url")
            summary = article.get("description")
            source_name = article.get("source", {}).get("name")
            published_at_str = article.get("publishedAt") # ISO 8601 format

            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source_name if source_name else "NewsAPI.org",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"NewsAPI.org World News fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for NewsAPI.org World News: {val_err}")
        return []
    except Exception as e:
        print(f"NewsAPI.org World News unexpected error: {e}")
        return []