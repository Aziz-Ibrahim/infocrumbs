from django.utils.timezone import now
from django.utils.text import slugify

from crumbs.models import Crumb
from preferences.models import Topic
from pipeline.utils import summarize_text


def handle_trivia_data(fact_list):
    """
    Handles trivia-related crumbs by creating or updating Crumb objects
    based on the provided crumb data list. Each crumb is associated with
    the 'trivia-and-fun' topic. If the topic does not exist, it will
    print an error message and return 0.
    :param crumb_data_list: List of dictionaries containing crumb data.
    :return: Number of Crumb objects created.
    """
    topic, _ = Topic.objects.get_or_create(name="trivia and fun", defaults={
        "slug": slugify("trivia and fun")
    })

    created_count = 0
    for fact in fact_list:
        if Crumb.objects.filter(summary=fact["summary"]).exists():
            continue

        try:
            Crumb.objects.create(
                title=fact["title"],
                summary=summarize_text(fact["summary"]),
                url=fact["url"],
                source=fact["source"],
                topic=topic,
                published_at=now()
            )
            created_count += 1
        except Exception as e:
            print(f"Error saving trivia crumb: {e}")

    return created_count
