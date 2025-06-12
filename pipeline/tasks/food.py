import requests
from django.conf import settings
from datetime import datetime, timezone


def fetch_spoonacular_random_recipes(limit=5):
    """
    Fetches random recipes from Spoonacular API.

    Args:
        limit (int): The number of random recipes to fetch.

    Returns:
        list: A list of dictionaries containing recipe details.
    """
    crumbs = []
    try:
        if not settings.SPOONACULAR_API_KEY:
            raise ValueError(
                "SPOONACULAR_API_KEY is not set in Django settings.")
        if not settings.SPOONACULAR_API_URL:
            raise ValueError(
                "SPOONACULAR_API_URL is not set in Django settings.")

        # Spoonacular's random endpoint supports a 'number' parameter
        url = f"{settings.SPOONACULAR_API_URL}&number={limit}"

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        for recipe in data.get("recipes", []):
            title = recipe.get("title")
            url = recipe.get("sourceUrl")
            # Combine summary fields for richer content
            summary = (
                f"Servings: {recipe.get('servings', 'N/A')}. "
                f"Prep Time: {recipe.get('readyInMinutes', 'N/A')} mins. "
                f"Cuisines: {', '.join(recipe.get('cuisines', []))}. "
                f"Dietary: {', '.join(recipe.get('diets', []))}. "
                f"Instructions: {recipe.get('instructions', '')[:500]}..."
            )
            source = recipe.get("sourceName", "Spoonacular")
            # Spoonacular recipes usually don't have a specific published_at
            published_at = None

            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source,
                "published_at": published_at,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Spoonacular Recipes fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for Spoonacular Recipes: {val_err}")
        return []
    except Exception as e:
        print(f"Spoonacular Recipes unexpected error: {e}")
        return []


def fetch_newsdata_food_drink_news():
    """
    Fetches food and drink news articles from NewsData.io API.

    Returns:
        list: A list of dictionaries containing article details.
    """
    crumbs = []
    try:
        url = getattr(settings, 'NEWSDATA_FOOD_DRINK_URL', None)
        if not url:
            raise ValueError(
                "NEWSDATA_FOOD_DRINK_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        for article in data.get("results", []):
            title = article.get("title")
            url = article.get("link")
            summary = article.get("description")
            source = article.get("source_id")
            published_at_str = article.get("pubDate")

            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source if source else "NewsData.io Food & Drink",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"NewsData.io Food & Drink News fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(
            f"Configuration error for NewsData.io Food & Drink News: {val_err}"
            )
        return []
    except Exception as e:
        print(f"NewsData.io Food & Drink News unexpected error: {e}")
        return []