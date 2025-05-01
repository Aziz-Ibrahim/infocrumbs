import os
import requests

def get_quote():
    url = os.environ.get('APININJA_API_URL')
    headers = {'X-Api-Key': os.environ.get('APININJA_API_KEY')}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []
