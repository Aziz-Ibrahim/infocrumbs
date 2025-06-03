from django.utils.dateparse import parse_datetime

from pipeline.utils import summarize_text
from crumbs.models import Crumb
from preferences.models import Topic


def handle_finance_crumbs(crumb_data_list):
    """
    Handles finance-related crumbs by creating or updating Crumb objects
    based on the provided crumb data list. Each crumb is associated with
    the 'stock-crypto-finance' topic. If the topic does not exist, it will
    print an error message and return 0.
    :param crumb_data_list: List of dictionaries containing crumb data.
    :return: Number of Crumb objects created.
    """
    topic = Topic.objects.filter(slug="stock-crypto-finance").first()
    if not topic:
        print("Topic 'finance' not found.")
        return 0

    created_count = 0
    for data in crumb_data_list:
        crumb, created = Crumb.objects.get_or_create(
            title=data["title"],
            summary=summarize_text(data.get("summary") or data.get("description", "")),
            url=data["url"],
            defaults={
                "source": data["source"],
                "topic": topic,
                "published_at": parse_datetime(data["published_at"]) if data["published_at"] else None,
            }
        )
        if created:
            created_count += 1

    return created_count
