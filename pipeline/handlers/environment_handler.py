from django.utils.text import slugify
from django.utils.dateparse import parse_datetime
from pipeline.utils import summarize_text

from crumbs.models import Crumb
from preferences.models import Topic

def handle_environment_articles(articles):
    topic, _ = Topic.objects.get_or_create(
        name="environment",
        defaults={"slug": slugify("environment")}
    )

    created_count = 0
    for article in articles:
        title = article.get("title", "")[:255]
        url = article.get("link")

        if Crumb.objects.filter(title=title, url=url).exists():
            continue

        try:
            Crumb.objects.create(
                title=title,
                summary=summarize_text(article.get("description", "")),
                url=url,
                source=article.get("source_id", "NewsData.io"),
                topic=topic,
                published_at=parse_datetime(article.get("pubDate")),
            )
            created_count += 1
        except Exception as e:
            print(f"Error saving environment article: {e}")

    return created_count
