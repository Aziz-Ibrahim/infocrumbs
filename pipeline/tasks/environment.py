import requests
from django.conf import settings

def fetch_environment_news():
    try:
        response = requests.get(settings.NEWSDATA_API_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        print(f"NewsData.io fetch error: {e}")
        return []
