from django.core.management.base import BaseCommand

from pipeline.tasks.newsapi import fetch_newsapi_articles
from pipeline.tasks.lastfm import fetch_lastfm_tracks

from pipeline.handlers.news_handler import handle_news_data
from pipeline.handlers.music_handler import handle_music_data


class Command(BaseCommand):
    """
    Command to fetch new crumbs from multiple APIs
    and save them to the database.
    """
    help = 'Fetch new crumbs from external APIs and save them'

    def handle(self, *args, **kwargs):
        self.stdout.write(" Starting to fetch crumbs...")

        total_created = 0

        # Fetch and handle news
        self.stdout.write(" Fetching world news...")
        news_articles = fetch_newsapi_articles()
        news_count = handle_news_data(news_articles)
        self.stdout.write(
            self.style.SUCCESS(f" {news_count} news crumbs added.")
            )
        total_created += news_count

        # Fetch and handle music
        self.stdout.write(" Fetching music data...")
        music_tracks = fetch_lastfm_tracks(limit=10)
        music_count = handle_music_data(music_tracks)
        self.stdout.write(
            self.style.SUCCESS(f" {music_count} music crumbs added.")
            )
        total_created += music_count

        self.stdout.write(
            self.style.SUCCESS(f" Total crumbs added: {total_created}")
            )
