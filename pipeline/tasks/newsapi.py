import requests
from django.conf import settings


def fetch_newsapi_articles():
    """
    Fetches the latest articles from NewsAPI and returns a list of dictionaries
    containing article details such as title, summary, URL, source,
    published date, and topic slug.
    """
    url = settings.NEWS_API_URL
    response = requests.get(url)
    if response.status_code != 200:
        return []

    data = response.json()
    articles = data.get('articles', [])
    return [
        {
            'title': a['title'],
            'summary': a['description'],
            'url': a['url'],
            'source': a['source']['name'],
            'published_at': a['publishedAt'],
            'topic_slug': 'world_news'
        }
        for a in articles if a.get('title') and a.get('url')
    ]
