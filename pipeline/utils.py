import requests
from django.conf import settings

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


def tag_crumb(crumb, topic):
    """
    Tag a crumb based on its topic.
    Placeholder for future tagging logic.
    """
    pass  # Implement keyword or NLP tagging here if needed
