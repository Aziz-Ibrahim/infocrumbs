import requests
import html
from django.conf import settings
from datetime import datetime, timezone


def fetch_useless_facts():
    """
    Fetches a random useless fact.

    Returns:
        list: A list containing one dictionary with fact details.
    """
    crumbs = []
    try:
        url = getattr(settings, 'USELESS_FACTS_API_URL', None)
        if not url:
            raise ValueError(
                "USELESS_FACTS_API_URL is not set in Django settings.")

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        fact_text = data.get("text")
        fact_source = data.get("source")
        fact_source_url = data.get("source_url")

        if fact_text:
            crumbs.append({
                "title": f"Useless Fact: {fact_text[:50]}...",
                "summary": fact_text,
                "url": fact_source_url,
                "source": fact_source if fact_source else "Useless Facts API",
                "published_at": None,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Useless Facts fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for Useless Facts: {val_err}")
        return []
    except Exception as e:
        print(f"Useless Facts unexpected error: {e}")
        return []


def fetch_chuck_norris_jokes():
    """
    Fetches a random Chuck Norris joke.

    Returns:
        list: A list containing one dictionary with joke details.
    """
    crumbs = []
    try:
        url = getattr(settings, 'CHUCKNORRIS_API_URL', None)
        if not url:
            raise ValueError(
                "CHUCKNORRIS_API_URL is not set in Django settings.")

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        joke_value = data.get("value")
        joke_url = data.get("url")

        if joke_value:
            crumbs.append({
                "title": "Chuck Norris Fact",
                "summary": joke_value,
                "url": joke_url,
                "source": "Chuck Norris Jokes",
                "published_at": None,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Chuck Norris Jokes fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for Chuck Norris Jokes: {val_err}")
        return []
    except Exception as e:
        print(f"Chuck Norris Jokes unexpected error: {e}")
        return []


def fetch_open_trivia(amount=5):
    """
    Fetches trivia questions from Open Trivia Database.
    Defaults to category 26 (Celebrities) as per your setting.

    Args:
        amount (int): Number of trivia questions to fetch. Max 50.

    Returns:
        list: A list of dictionaries containing trivia question details.
    """
    crumbs = []
    try:
        url = getattr(settings, 'OPEN_TRIVIA_API_URL', None)
        if not url:
            raise ValueError(
                "OPEN_TRIVIA_API_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("response_code") != 0:
            print(f"Open Trivia API error: {data.get('response_code')}")
            return []

        for question_data in data.get("results", []):
            category = html.unescape(question_data.get("category", "Trivia"))
            difficulty = html.unescape(question_data.get("difficulty", "easy"))
            question = html.unescape(question_data.get("question", ""))
            correct_answer = html.unescape(
                question_data.get("correct_answer", ""))

            if not question:
                continue

            title = f"{category} ({difficulty.capitalize()}) Trivia"
            summary = f"Question: {question}\nAnswer: {correct_answer}"
            
            crumbs.append({
                "title": title[:255],
                "summary": summary,
                "url": "https://opentdb.com/",  # Generic link to the source
                "source": "Open Trivia DB",
                "published_at": None,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Open Trivia fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for Open Trivia: {val_err}")
        return []
    except Exception as e:
        print(f"Open Trivia unexpected error: {e}")
        return []
