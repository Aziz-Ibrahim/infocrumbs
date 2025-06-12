import requests
from django.conf import settings
from datetime import datetime, timezone


def fetch_newsapi_cars_transport_news():
    """
    Fetches cars and transport news articles from NewsAPI.org API
    using the /v2/everything endpoint.

    Returns:
        list: A list of dictionaries containing article details.
    """
    crumbs = []
    try:
        url = getattr(settings, 'NEWSAPI_CARS_TRANSPORT_URL', None)
        if not url:
            raise ValueError(
                "NEWSAPI_CARS_TRANSPORT_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        # NewsAPI.org returns results under the 'articles' key
        for article in data.get("articles", []):
            title = article.get("title")
            url = article.get("url")
            summary = article.get("description")
            source_name = article.get("source", {}).get("name")
            published_at_str = article.get("publishedAt")

            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source_name if source_name else
                          "NewsAPI.org Cars & Transport",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"NewsAPI.org Cars & Transport News fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for NewsAPI.org Cars & Transport News: "
              f"{val_err}")
        return []
    except Exception as e:
        print(f"NewsAPI.org Cars & Transport News unexpected error: {e}")
        return []