import requests
from django.conf import settings
from datetime import datetime, timezone # Ensure timezone is imported


def fetch_thenewsapi_sports():
    """
    Fetches general sports news articles from TheNewsAPI.

    Returns:
        list: A list of dictionaries containing article details.
    """
    try:
        url = getattr(settings, 'THENEWSAPI_SPORTS_URL', None)
        if not url:
            raise ValueError(
                "THENEWSAPI_SPORTS_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        crumbs = []
        for article in data.get("data", []):
            title = article.get("title")
            url = article.get("url")
            summary = article.get("description")
            source = article.get("source")
            published_at_str = article.get("published_at")

            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source if source else "TheNewsAPI",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"TheNewsAPI Sports fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for TheNewsAPI Sports: {val_err}")
        return []
    except Exception as e:
        print(f"TheNewsAPI Sports unexpected error: {e}")
        return []


def fetch_newsdata_fitness():
    """
    Fetches fitness-related news articles from NewsData.io API
    using a broader set of keywords and categories.

    Returns:
        list: A list of dictionaries containing article details.
    """
    try:
        url = getattr(settings, 'NEWSDATA_FITNESS_URL', None)
        if not url:
            raise ValueError(
                "NEWSDATA_FITNESS_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        crumbs = []
        for article in data.get("results", []):
            title = article.get("title")
            url = article.get("link") # NewsData.io uses 'link' for URL
            summary = article.get("description")
            source = article.get("source_id") # NewsData.io uses 'source_id'
            published_at_str = article.get("pubDate") # NewsData.io uses 'pubDate'

            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source if source else "NewsData.io Fitness",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"NewsData.io Fitness fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for NewsData.io Fitness: {val_err}")
        return []
    except Exception as e:
        print(f"NewsData.io Fitness unexpected error: {e}")
        return []