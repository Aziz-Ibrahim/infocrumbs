import os
import requests

def authenticate_lastfm():
    url = os.environ.get('LASTFM_API_URL')
    try:
        return url  # For LastFM, auth is via browser
    except Exception:
        return None
