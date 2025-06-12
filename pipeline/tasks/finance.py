import requests
from django.conf import settings
from datetime import datetime, timezone


def fetch_finnhub_general_news():
    """
    Fetches general market news articles from Finnhub API.

    Returns:
        list: A list of dictionaries containing article details.
    """
    try:
        url = getattr(settings, 'FINNHUB_API_URL', None)
        if not url:
            raise ValueError("FINNHUB_API_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        crumbs = []
        # Finnhub general news returns a list of articles
        for article in data:
            title = article.get("headline")
            url = article.get("url")
            summary = article.get("summary")
            source = article.get("source")
            datetime_unix = article.get("datetime")

            published_at_str = None
            if datetime_unix:
                published_at_str = datetime.fromtimestamp(
                    datetime_unix, tz=timezone.utc).isoformat()


            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source if source else "Finnhub",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Finnhub General News fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for Finnhub General News: {val_err}")
        return []
    except Exception as e:
        print(f"Finnhub General News unexpected error: {e}")
        return []