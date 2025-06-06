from preferences.models import Topic
from django.utils.text import slugify
from django.utils.dateparse import parse_datetime

from crumbs.models import Crumb
from pipeline.utils import summarize_text


def handle_technology_news(articles):
    """
    Save Mediastack tech news articles to Crumb objects.
    """
    topic, _ = Topic.objects.get_or_create(name="technology", defaults={
        "slug": slugify("technology")
    })

    created_count = 0
    for article in articles:
        title = article.get("title")
        url = article.get("url")

        if not title or not url or \
            Crumb.objects.filter(title=title, url=url).exists():
            continue

        summary = summarize_text(
            article.get("description", "") or article.get("title", "")
            )

        try:
            Crumb.objects.create(
                title=title[:255],
                summary=summary,
                url=url,
                source=article.get("source", "Mediastack"),
                topic=topic,
                published_at=parse_datetime(article.get("published_at"))
            )
            created_count += 1
        except Exception as e:
            print(f"Error saving tech crumb: {e}")
            continue

    return created_count
