import os
import requests

def get_sportmonks_livescores():
    url = os.environ.get('SPORTMONKS_API_URL')
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception:
        return []