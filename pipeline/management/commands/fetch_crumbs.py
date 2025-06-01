from django.core.management.base import BaseCommand
from crumbs.models import Crumb
from preferences.models import Topic
from pipeline.tasks.newsapi import fetch_newsapi_articles


class Command(BaseCommand):
    """
    Command to fetch new crumbs from external APIs
    and save them to the database.
    """
    help = 'Fetch new crumbs from external APIs'

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching crumbs...")

        all_articles = fetch_newsapi_articles()
        created_count = 0

        for article in all_articles:
            topic = Topic.objects.filter(slug=article['topic_slug']).first()
            if not topic:
                continue

            crumb, created = Crumb.objects.get_or_create(
                title=article['title'],
                defaults={
                    'summary': article['summary'],
                    'url': article['url'],
                    'source': article['source'],
                    'topic': topic,
                    'published_at': article['published_at'],
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f"{created_count} crumbs added."))
