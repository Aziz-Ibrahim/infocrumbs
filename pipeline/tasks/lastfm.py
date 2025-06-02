import requests
from django.conf import settings


def fetch_lastfm_tracks(limit=10):
    """
    Fetches the top tracks from Last.fm.
    Args:
        limit (int): The number of top tracks to fetch. Default is 10.
    Returns:
        list: A list of dictionaries containing track information.
    """
    url = (
        f"http://ws.audioscrobbler.com/2.0/"
        f"?method=chart.gettoptracks"
        f"&api_key={settings.LASTFM_API_KEY}"
        f"&format=json"
        f"&limit={limit}"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        tracks = data.get("tracks", {}).get("track", [])

        return [
            {
                "title": track["name"],
                "artist": track["artist"]["name"],
                "url": track["url"],
                "listeners": track.get("listeners"),
                "topic_slug": "music"
            }
            for track in tracks if track.get("name") and track.get("url")
        ]
    except Exception as e:
        print(f"Last.fm fetch error: {e}")
        return []
