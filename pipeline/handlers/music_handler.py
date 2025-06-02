from crumbs.models import Crumb
from preferences.models import Topic
from django.utils.text import slugify
from django.utils.timezone import now


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
        if Crumb.objects.filter(title=title).exists():
            continue

        crumb = Crumb.objects.create(
            title=title,
            summary=f"A popular track on Last.fm with {track.get('listeners', 0)} listeners.",
            url=track["url"],
            source="Last.fm",
            topic=topic,
            published_at=now()
        )
        created_count += 1

    return created_count
