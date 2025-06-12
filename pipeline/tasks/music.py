import requests
import time
from django.conf import settings
from datetime import datetime, timezone


def fetch_lastfm_top_artists_bios(limit=10):
    """
    Fetches top artists from Last.fm and then retrieves their biographies.

    Args:
        limit (int): The maximum number of top artists to fetch.

    Returns:
        list: A list of dictionaries containing artist details
              (title, summary, url, source, published_at).
    """
    crumbs = []
    try:
        if not settings.LASTFM_API_KEY:
            raise ValueError("LASTFM_API_KEY is not set in Django settings.")
        if not settings.LASTFM_BASE_URL:
            raise ValueError("LASTFM_BASE_URL is not set in Django settings.")

        # 1. Get top artists
        top_artists_url = (
            f"{settings.LASTFM_BASE_URL}?"
            f"method=chart.gettopartists&api_key={settings.LASTFM_API_KEY}"
            f"&format=json&limit={limit}"
        )
        response = requests.get(top_artists_url, timeout=10)
        response.raise_for_status()
        top_artists_data = response.json()

        artists = top_artists_data.get("artists", {}).get("artist", [])

        # 2. For each artist, get their detailed info (including bio)
        for artist in artists:
            artist_name = artist.get("name")
            artist_url = artist.get("url")

            if not artist_name:
                continue

            # Add a small delay to respect Last.fm rate limits (5 requests/second)
            time.sleep(0.2)

            artist_info_url = (
                f"{settings.LASTFM_BASE_URL}?"
                f"method=artist.getInfo&artist="
                f"{requests.utils.quote(artist_name)}"
                f"&api_key={settings.LASTFM_API_KEY}&format=json"
            )
            info_response = requests.get(artist_info_url, timeout=10)
            info_response.raise_for_status()
            artist_detail_data = info_response.json()

            bio_summary = ""
            if artist_detail_data.get("artist", {}).get("bio", {}).get("summary"):
                # Last.fm bios often have a trailing "Read more" link, remove it
                bio_summary = artist_detail_data["artist"]["bio"]["summary"].split(
                    '<a href="https://www.last.fm/music/')[0].strip()

            # Last.fm doesn't provide a direct published_at for artist bios.
            published_at = None

            crumbs.append({
                "title": f"Artist Profile: {artist_name}",
                "summary": bio_summary,
                "url": artist_url,
                "source": "Last.fm",
                "published_at": published_at,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"Last.fm fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for Last.fm: {val_err}")
        return []
    except Exception as e:
        print(f"Last.fm unexpected error: {e}")
        return []


def fetch_newsdata_music_news():
    """
    Fetches music-related news articles from NewsData.io API.

    Returns:
        list: A list of dictionaries containing article details.
    """
    crumbs = []
    try:
        url = getattr(settings, 'NEWSDATA_MUSIC_NEWS_URL', None)
        if not url:
            raise ValueError(
                "NEWSDATA_MUSIC_NEWS_URL is not set in Django settings.")

        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        for article in data.get("results", []):
            title = article.get("title")
            url = article.get("link")
            summary = article.get("description")
            source = article.get("source_id")
            published_at_str = article.get("pubDate")

            if not title or not url:
                continue

            crumbs.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": source if source else "NewsData.io Music",
                "published_at": published_at_str,
            })
        return crumbs
    except requests.exceptions.RequestException as req_err:
        print(f"NewsData.io Music News fetch error: {req_err}")
        return []
    except ValueError as val_err:
        print(f"Configuration error for NewsData.io Music News: {val_err}")
        return []
    except Exception as e:
        print(f"NewsData.io Music News unexpected error: {e}")
        return []