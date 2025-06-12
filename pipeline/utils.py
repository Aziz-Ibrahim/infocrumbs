# pipeline/utils.py

import requests
import json
from django.conf import settings

# Define constants for Hugging Face API
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
# Max characters to send for summarization. Adjust as needed.
MAX_SUMMARY_INPUT_LENGTH = 1000
# Timeout for the API request in seconds
HF_API_TIMEOUT = 30


def summarize_text(text):
    """
    Sends text to Hugging Face API for summarization.
    Truncates text to MAX_SUMMARY_INPUT_LENGTH before sending.
    Returns an empty string if summarization fails or times out.
    """
    if not text:
        return ""

    # Ensure API key is set
    api_key = getattr(settings, 'HF_API_TOKEN', None)
    if not api_key:
        print("HuggingFace API key is not set in Django settings.")
        return ""

    headers = {"Authorization": f"Bearer {api_key}"}

    # Truncate text to avoid excessively long inputs
    truncated_text = text[:MAX_SUMMARY_INPUT_LENGTH]

    payload = {"inputs": truncated_text}

    try:
        response = requests.post(
            HUGGINGFACE_API_URL,
            headers=headers,
            json=payload,
            timeout=HF_API_TIMEOUT  # Use the defined timeout
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        result = response.json()

        if result and isinstance(result, list) and result[0].get("summary_text"):
            return result[0]["summary_text"]
        return ""  # Return empty if no summary text found
    except requests.exceptions.Timeout:
        print(f"HuggingFace summarization error: Read timed out. "
              f"(timeout={HF_API_TIMEOUT}s)")
        return ""  # Return empty string on timeout
    except requests.exceptions.RequestException as e:
        print(f"HuggingFace summarization API request error: {e}")
        return ""  # Return empty string on other request errors
    except json.JSONDecodeError as e:
        print(f"HuggingFace summarization JSON decoding error: {e}")
        return ""
    except Exception as e:
        print(f"Unexpected HuggingFace summarization error: {e}")
        return ""


def clean_text(text):
    """
    Cleans the input text by removing leading/trailing whitespace,
    splitting into sentences, and removing duplicates.
    """
    if not text:
        return ""
    # Simple split and dedup by sentences. Consider more robust NLP for production.
    parts = text.strip().split('. ')
    seen = set()
    deduped = []
    for sentence in parts:
        if sentence and sentence not in seen:
            seen.add(sentence)
            deduped.append(sentence)
    return '. '.join(deduped).strip()


def tag_crumb_text(text):
    """
    Attempt to match crumb text to a topic by checking for keywords.
    Returns the first matching Topic object, or None if no match is found.
    """
    from preferences.models import Topic # Import here to avoid circular dependencies

    if not text:
        return None

    keywords_map = {
        "world-news": [
            "breaking", "headline", "report", "journalist"
            ],
        "music": [
            "song", "album", "artist", "track"
            ],
        "sports-and-fitness": [
            "game", "match", "team", "fitness", "athlete"
            ],
        "stock-crypto-finance": [
            "market", "stock", "crypto", "investment", "economy"
            ],
        "food-and-drink": [
            "recipe", "meal", "ingredient", "cooking"
            ],
        "technology": [
            "AI", "tech", "gadget", "software", "hardware"
            ],
        "plants-and-gardening": [
            "plant", "soil", "water", "grow", "harvest"
            ],
        "environment": [
            "climate", "recycle", "sustainability", "biodiversity"
            ],
        "trivia-and-fun": [
            "fact", "joke", "trivia", "laugh", "weird"
            ],
    }

    text_lower = text.lower()
    for slug, keywords in keywords_map.items():
        if any(keyword in text_lower for keyword in keywords):
            # Return the Topic object directly
            return Topic.objects.filter(slug=slug).first()

    return None