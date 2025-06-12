import requests
from django.conf import settings
from datetime import datetime, timezone


def fetch_perenual_guides():
    """
    Fetches care guides from Perenual API and returns a list of dictionaries
    containing article details for plants and gardening topics.
    """
    try:
        url = settings.PERENUAL_API_URL
        perenual_guide_base_url = getattr(
            settings, 'PERENUAL_GUIDE_BASE_URL', 'https://perenual.com/guide/'
            )

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        crumbs = []
        for guide in data.get("data", []):
            if guide.get("care_guide"):
                item_url = f"{perenual_guide_base_url}{guide.get('slug')}" if \
                           guide.get('slug') else ""

                published_at = None

                crumbs.append({
                    "title": guide.get("common_name", "Care Guide"),
                    "summary": guide.get("care_guide", {}).get(
                        "description", ""
                    ),
                    "url": item_url,
                    "source": "Perenual",
                    "published_at": published_at,
                })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Perenual API request error: {req_err}")
        return []
    except ValueError as json_err:
        print(f"Perenual JSON decoding error: {json_err}")
        return []
    except Exception as e:
        print(f"Perenual unexpected error: {e}")
        return []


def fetch_trefle_plants():
    """
    Fetches plant information from Trefle API and returns a list of
    dictionaries containing article details for plants and gardening topics.
    """
    try:
        url = settings.TREFLE_API_URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        crumbs = []
        for plant in data.get("data", []):
            published_at = None

            crumbs.append({
                "title": plant.get("common_name", "Plant Info"),
                "summary": plant.get("scientific_name", ""),
                "url": plant.get("links", {}).get("self", ""),
                "source": "Trefle",
                "published_at": published_at,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Trefle API request error: {req_err}")
        return []
    except ValueError as json_err:
        print(f"Trefle JSON decoding error: {json_err}")
        return []
    except Exception as e:
        print(f"Trefle unexpected error: {e}")
        return []


def fetch_permapeople_plants():
    """
    Fetches plant information from PermaPeople API and returns a list of
    dictionaries containing article details for plants and gardening topics.
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

        crumbs = []
        for item in data.get("data", []):
            # PermaPeople API might not provide 'published_at'
            published_at = None

            crumbs.append({
                "title": item.get("name", "PermaPlant Info"),
                "summary": item.get("description", ""),
                "url": f"https://permapeople.org/plants/{item.get('id')}",
                "source": "PermaPeople",
                "published_at": published_at,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"PermaPeople API request error: {req_err}")
        return []
    except ValueError as json_err:
        print(f"PermaPeople JSON decoding error: {json_err}")
        return []
    except Exception as e:
        print(f"PermaPeople unexpected error: {e}")
        return []
