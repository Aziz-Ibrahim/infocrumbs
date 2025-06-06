import requests
from django.conf import settings

def fetch_foodcrumbs():
    """
    Fetch random recipes from Spoonacular.
    """
    url = settings.SPOONACULAR_API_URL
    params = {
        "apiKey": settings.SPOONACULAR_API_KEY,
        "number": 10
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data.get("recipes", [])
    except Exception as e:
        print(f"FoodCrumbs fetch error: {e}")
        return []
