import requests
from django.conf import settings
from datetime import datetime, timedelta, timezone

def fetch_finance_news():
    """
    Fetch recent financial news articles from Finnhub.
    """
    try:
        today = datetime.today().strftime('%Y-%m-%d')
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        base_url = "https://finnhub.io/api/v1/company-news"
        symbol = "AAPL"
        url = f"{base_url}?symbol={symbol}&from={yesterday}&to={today}&token={settings.FINNHUB_API_KEY}"

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json()

        crumbs = []
        for article in articles:
            if not article.get("headline") or not article.get("url"):
                continue

            crumbs.append({
                "title": article["headline"],
                "summary": article.get("summary", "No summary available."),
                "url": article["url"],
                "source": article.get("source", "Finnhub"),
                "published_at": datetime.fromtimestamp(article["datetime"], tz=timezone.utc).isoformat(),
                "topic_slug": "finance"
            })

        return crumbs

    except Exception as e:
        print(f"Finnhub fetch error: {e}")
        return []
