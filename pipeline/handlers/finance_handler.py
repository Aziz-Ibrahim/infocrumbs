from crumbs.models import Crumb
from preferences.models import Topic
from django.utils.dateparse import parse_datetime

def handle_finance_crumbs(crumb_data_list):
    topic = Topic.objects.filter(slug="stock-crypto-finance").first()
    if not topic:
        print("Topic 'finance' not found.")
        return 0

    created_count = 0
    for data in crumb_data_list:
        crumb, created = Crumb.objects.get_or_create(
            title=data["title"],
            url=data["url"],
            defaults={
                "summary": data["summary"],
                "source": data["source"],
                "topic": topic,
                "published_at": parse_datetime(data["published_at"]) if data["published_at"] else None,
            }
        )
        if created:
            created_count += 1

    return created_count
