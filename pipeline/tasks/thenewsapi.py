import requests
from django.conf import settings


def fetch_sports_news():
    """
    Fetches general sports news articles from TheNewsAPI.
    """
    try:
        url = settings.THENEWSAPI_SPORTS_URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = []
        for article in data.get("data", []):
            articles.append({
                "title": article.get("title"),
                "summary": article.get("description"),
                "url": article.get("url"),
                "image_url": article.get("image_url"),
                "source": article.get("source"),
                "published_at": article.get("published_at"),
                "topic_slug": "sports-and-fitness"
            })

        return articles

    except Exception as e:
        print(f"TheNewsAPI Sports fetch error: {e}")
        return []
