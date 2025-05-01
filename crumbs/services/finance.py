import os
import requests

def get_alpha_vantage_data():
    url = os.environ.get('ALPHA_VANTAGE_API_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}

def get_finnhub_quote():
    url = os.environ.get('FINNHUB_API_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}
