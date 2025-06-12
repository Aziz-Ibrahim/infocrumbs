import requests
from django.conf import settings
from datetime import datetime, timezone


def fetch_mediastack_technology_news():
    """
    Fetches technology news articles from Mediastack API,
    filtered to English language.

    Returns:
        list: A list of dictionaries containing article details.
    """
    crumbs = []
    try:
        url = getattr(settings, 'MEDIASTACK_TECHNOLOGY_URL', None)
        if not url:
            raise ValueError(
                "MEDIASTACK_TECHNOLOGY_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Mediastack returns results under the 'data' key
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
                "source": source if source else "Mediastack Technology",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Mediastack Technology News fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for Mediastack Technology News: {val_err}")
        return []
    except Exception as e:
        print(f"Mediastack Technology News unexpected error: {e}")
        return []