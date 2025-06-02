import requests
from django.conf import settings


def fetch_sportmonks_events():
    """
    Fetch sports events from the SportMonks API and return
    a list of dictionaries structured for creating crumbs.
    """
    try:
        url = settings.SPORTMONKS_API_URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        events = []
        for match in data.get("data", []):
            home = match.get("localTeam", {}).get("data", {}).get("name", "Unknown")
            away = match.get("visitorTeam", {}).get("data", {}).get("name", "Unknown")
            date = match.get("time", {}).get("starting_at", {}).get("date")
            league = match.get("league", {}).get("data", {}).get("name", "Unknown")
            summary = f"{home} vs {away} - {league} on {date}"

            events.append({
                "title": f"{home} vs {away}",
                "summary": summary,
                "source": "SportMonks",
                "published_at": date,
                "url": f"https://sportmonks.com/api-docs/football/{match.get('id', '')}",  # Optional link
                "topic_slug": "sports-and-fitness"
            })
        return events

    except Exception as e:
        print(f"SportMonks fetch error: {e}")
        return []
