import requests
from django.conf import settings

from preferences.models import Topic


HF_API_URL = settings.HF_API_URL
HF_API_TOKEN = settings.HF_API_TOKEN

headers = {
    "Authorization": f"Bearer {HF_API_TOKEN}"
}

def summarize_text(text, min_length=20, max_length=100):
    """
    Sends text to Hugging Face's BART summarization model
    and returns the summary.
    """
    if not text:
        return ""

    text = (text or "").strip()
    if len(text) > 500:
        text = text[:500] + "..."

    payload = {
        "inputs": text,
        "parameters": {
            "min_length": min_length,
            "max_length": max_length
        }
    }

    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=15
            )
        response.raise_for_status()
        result = response.json()
        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]
        return ""
    except Exception as e:
        print(f"HuggingFace summarization error: {e}")
        return ""


def clean_text(text):
    """
    Cleans the input text by removing leading/trailing whitespace,
    splitting into sentences, and removing duplicates.
    """
    if not text:
        return ""
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
    if not text:
        return []

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
        # Placeholder for any additional topics
    }

    text_lower = text.lower()
    for slug, keywords in keywords_map.items():
        if any(keyword in text_lower for keyword in keywords):
            return Topic.objects.filter(slug=slug).first()

    return None

