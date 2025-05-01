import os
import requests

def get_newsapi_headlines():
    url = os.environ.get('NEWS_API_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('articles', [])
    except Exception:
        return []

def get_thenewsapi_headlines():
    url = os.environ.get('THE_NEWS_API_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception:
        return []
