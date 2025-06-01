import requests
import os


NEWS_API_URL = os.getenv("NEWS_API_URL")

def fetch_news_articles():
    """
    Fetches articles from NewsAPI and returns a list of dictionaries
    with title, description, url, and published date.
    """
    try:
        response = requests.get(NEWS_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        articles = []
        for article in data.get("articles", []):
            articles.append({
                "title": article.get("title"),
                "summary": article.get("description"),
                "url": article.get("url"),
                "image_url": article.get("urlToImage"),
                "published_at": article.get("publishedAt"),
                "source_name": article.get("source", {}).get("name"),
            })
        return articles
    except Exception as e:
        print(f"NewsAPI fetch error: {e}")
        return []
