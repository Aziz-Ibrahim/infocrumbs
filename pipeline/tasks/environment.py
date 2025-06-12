import requests
from django.conf import settings


def fetch_environment_news():
    """
    Fetches environment-related news articles from NewsData.io API.
    """
    try:
        url = getattr(settings, 'NEWSDATA_API_URL', None)
        if not url:
            raise ValueError("NEWSDATA_API_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        return data.get("results", [])
    except requests.exceptions.RequestException as req_err:
        print(f"NewsData.io API request error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for NewsData.io fetch: {val_err}")
        return []
    except Exception as e:
        print(f"NewsData.io unexpected error: {e}")
        return []