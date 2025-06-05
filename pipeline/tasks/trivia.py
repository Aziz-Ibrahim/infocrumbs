import requests
from django.conf import settings


def fetch_trivia_facts():
    """
    Fetches from 2 APIs and returns a list of dictionaries
    containing details such as title, summary, URL, source,
    and published date.
    """
    facts = []

    # Useless Facts
    try:
        print("Fetching Useless Fact...")
        response = requests.get(settings.USELESS_FACTS_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        facts.append({
            "title": "Useless Fact",
            "summary": data.get("text", ""),
            "url": data.get("source_url", "https://uselessfacts.jsph.pl/"),
            "source": "Useless Facts",
        })
    except Exception as e:
        print(f"Useless Facts fetch error: {e}")

    # Chuck Norris Jokes
    try:
        print("Fetching Chuck Norris Joke...")
        response = requests.get(settings.CHUCKNORRIS_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        facts.append({
            "title": "Chuck Norris Joke",
            "summary": data.get("value", ""),
            "url": data.get("url", "https://api.chucknorris.io/"),
            "source": "Chuck Norris API",
        })
    except Exception as e:
        print(f"Chuck Norris API fetch error: {e}")

    return facts
