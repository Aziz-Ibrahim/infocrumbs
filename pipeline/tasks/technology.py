import requests
from django.conf import settings


def fetch_technology_news():
    """
    Fetch latest technology news from Mediastack API.
    """
    try:
        response = requests.get(settings.MEDIASTACK_TECHNOLOGY_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"Mediastack fetch error: {e}")
        return []
