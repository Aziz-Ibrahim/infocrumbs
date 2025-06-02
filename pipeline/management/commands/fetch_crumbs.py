from django.core.management.base import BaseCommand

from pipeline.tasks.newsapi import fetch_newsapi_articles
from pipeline.tasks.lastfm import fetch_lastfm_tracks

from pipeline.handlers.news_handler import handle_news_data
from pipeline.handlers.music_handler import handle_music_data

from pipeline.tasks.finnhub import fetch_finance_news
from pipeline.handlers.finance_handler import handle_finance_crumbs

from pipeline.tasks.thenewsapi import fetch_sports_news
from pipeline.handlers.sports_handler import save_sports_articles


class Command(BaseCommand):
    """
    Command to fetch new crumbs from multiple APIs
    and save them to the database.
    """
    help = 'Fetch new crumbs from external APIs and save them'

    def handle(self, *args, **kwargs):
        # Print a message indicating the start of the command
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

        # Fetch and handle finance
        self.stdout.write("Fetching finance news from Finnhub...")
        finance_data = fetch_finance_news()
        finance_added = handle_finance_crumbs(finance_data)
        self.stdout.write(
            self.style.SUCCESS(f"Finance crumbs added: {finance_added}")
            )

        self.stdout.write("Fetching sports and fitness articles...")
        sports_articles = fetch_sports_news()
        created = save_sports_articles(sports_articles)
        self.stdout.write(self.style.SUCCESS(f"{created} sports crumbs saved."))

        self.stdout.write(
            self.style.SUCCESS(f" Total crumbs added: {total_created}")
            )
