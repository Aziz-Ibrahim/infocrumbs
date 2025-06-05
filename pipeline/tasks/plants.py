import requests
from django.conf import settings


def fetch_perenual_guides():
    """
    Fetches the care and guide from Perenual API and returns
    a list of dictionaries containing article details such as title, summary,
    URL, source, published date, and topic slug.
    """
    try:
        url = settings.PARENUAL_API_URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [{
            "title": guide.get("common_name", "Care Guide"),
            "summary": guide.get("care_guide", {}).get("description", ""),
            "url": guide.get("slug", ""),
            "source": "Perenual"
        } for guide in data.get("data", []) if guide.get("care_guide")]
    except Exception as e:
        print(f"Perenual fetch error: {e}")
        return []


def fetch_trefle_plants():
    """
    Fetches the plant information from Trefle API and returns
    a list of dictionaries containing article details such as title, summary,
    URL, source, published date, and topic slug.
    """
    try:
        url = settings.TREFLE_API_URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [{
            "title": plant.get("common_name", "Plant Info"),
            "summary": plant.get("scientific_name", ""),
            "url": plant.get("links", {}).get("self", ""),
            "source": "Trefle"
        } for plant in data.get("data", [])]
    except Exception as e:
        print(f"Trefle fetch error: {e}")
        return []


def fetch_permapeople_plants():
    """
    Fetches the plant information from Perma People API and returns
    a list of dictionaries containing article details such as title, summary,
    URL, source, published date, and topic slug.
    """
    try:
        headers = {
            "x-permapeople-key-id": settings.PERMAPEOPLE_KEY_ID,
            "x-permapeople-key-secret": settings.PERMAPEOPLE_KEY_SECRET,
        }
        url = settings.PERMAPEOPLE_API_URL
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return [{
            "title": item.get("name", "PermaPlant Info"),
            "summary": item.get("description", ""),
            "url": f"https://permapeople.org/plants/{item.get('id')}",
            "source": "PermaPeople"
        } for item in data.get("data", [])]
    except Exception as e:
        print(f"PermaPeople fetch error: {e}")
        return []
