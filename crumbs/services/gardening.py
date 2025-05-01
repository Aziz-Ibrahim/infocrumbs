import os
import requests

def get_gardening_guides():
    url = os.environ.get('PARENUAL_API_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception:
        return []

def get_trefle_plants():
    url = os.environ.get('TREFLE_API_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception:
        return []

def get_permapeople_profiles():
    url = os.environ.get('PERMAPEOPLE_API_URL')
    headers = {
        'Authorization': f"{os.environ.get('PERMAPEOPLE_KEY_ID')}:{os.environ.get('PERMAPEOPLE_KEY_SECRET')}"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception:
        return []
