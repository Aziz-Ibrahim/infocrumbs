from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from pipeline.tasks.fetch_news import fetch_news_articles
from crumbs.models import Crumb
from preferences.models import Topic


class Command(BaseCommand):
    """
    Command to fetch articles from NewsAPI and save them as Crumbs.
    """

    help = "Fetch NewsAPI articles and save them as Crumbs"

    def handle(self, *args, **kwargs):
        articles = fetch_news_articles()
        if not articles:
            self.stdout.write(self.style.WARNING("No articles were fetched."))
            return

        topic_name = "world news"
        topic, _ = Topic.objects.get_or_create(name=topic_name)

        created_count = 0
        for article in articles:
            # Avoid duplicates
            if Crumb.objects.filter(
                title=article['title'],url=article['url']
                ).exists():
                continue

            try:
                crumb = Crumb.objects.create(
                    title=article["title"][:255],
                    summary=article["summary"] or "",
                    url=article["url"],
                    source=article["source_name"] or "Unknown",
                    topic=topic,
                    published_at=parse_datetime(article["published_at"]),
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Error saving article: {e}")
                    )

        self.stdout.write(
            self.style.SUCCESS(f"{created_count} new crumbs saved.")
        )
