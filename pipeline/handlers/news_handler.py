from crumbs.models import Crumb
from preferences.models import Topic
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify


def handle_news_data(article_list):
    """
    Process and save news articles into Crumb objects.
    """
    topic, _ = Topic.objects.get_or_create(name="world news", defaults={
        "slug": slugify("world news")
    })

    created_count = 0
    for article in article_list:
        if Crumb.objects.filter(
            title=article['title'],
            url=article['url']
            ).exists():
            continue

        try:
            crumb = Crumb.objects.create(
                title=article["title"][:255],
                summary=article["summary"] or "",
                url=article["url"],
                source=article["source"],
                topic=topic,
                published_at=parse_datetime(article["published_at"]),
            )
            created_count += 1
        except Exception as e:
            print(f"Error saving news article: {e}")

    return created_count
