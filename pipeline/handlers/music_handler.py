from django.utils.text import slugify
from django.utils.timezone import now

from crumbs.models import Crumb
from preferences.models import Topic
from pipeline.utils import summarize_text


def handle_music_data(track_list):
    """
    Process and save music data into Crumb objects.
    """
    topic, _ = Topic.objects.get_or_create(name="music", defaults={
        "slug": slugify("music")
    })

    created_count = 0
    for track in track_list:
        title = f"{track['title']} by {track['artist']}"
        if Crumb.objects.filter(title=title, url=track["url"]).exists():
            continue

        try:
            description = f"{track['title']} by {track['artist']} has {track.get('listeners', 'N/A')} listeners on Last.fm."
            summary = summarize_text(description)

            Crumb.objects.create(
                title=title,
                summary=summary,
                url=track["url"],
                source="Last.fm",
                topic=topic,
                published_at=now()
            )
            created_count += 1
        except Exception as e:
            print(f"Error saving music crumb: {e}")
            continue

    return created_count
