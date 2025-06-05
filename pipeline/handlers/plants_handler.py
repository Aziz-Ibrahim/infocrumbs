from crumbs.models import Crumb
from preferences.models import Topic
from django.utils.text import slugify
from django.utils.timezone import now
from pipeline.utils import summarize_text


def handle_plant_data(source, data_list):
    """
    Handles plants and gardening crumbs by creating or updating Crumb objects
    based on the provided crumb data list. Each crumb is associated with
    the 'plants-and-gardening' topic. If the topic does not exist, it will
    print an error message and return 0.
    :param crumb_data_list: List of dictionaries containing crumb data.
    :return: Number of Crumb objects created.
    """
    topic, _ = Topic.objects.get_or_create(
        name="plants and gardening", defaults={
        "slug": slugify("plants and gardening")
    })

    created_count = 0
    for item in data_list:
        if Crumb.objects.filter(title=item["title"], url=item["url"]).exists():
            continue

        try:
            Crumb.objects.create(
                title=item["title"][:255],
                summary=summarize_text(item.get("description", "")),
                url=item["url"],
                source=item["source"] if item.get("source") else source,
                topic=topic,
                published_at=now()
            )
            created_count += 1
        except Exception as e:
            print(f"Error saving plant crumb from {source}: {e}")
            continue

    return created_count
