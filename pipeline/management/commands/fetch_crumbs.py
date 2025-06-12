from django.core.management.base import BaseCommand

from pipeline.tasks import (
    plants,
    environment,
    sports,
    finance,
    )
from pipeline.handlers import (
    plants_handler,
    environment_handler,
    sports_handler,
    finance_handler,
    )

class Command(BaseCommand):
    help = 'Fetches crumbs from various sources and adds them to the database.'

    def handle(self, *args, **options):
        self.stdout.write("Starting crumb fetching process...")
        total_created = 0

        self.stdout.write("Fetching plant-related info...")

        perenual_data = plants.fetch_perenual_guides()
        created_perenual = plants_handler.handle_plant_data(
            "Perenual", perenual_data)
        self.stdout.write(
            self.style.SUCCESS(f"{created_perenual} plant crumbs saved from "
                               "Perenual.")
        )

        trefle_data = plants.fetch_trefle_plants()
        created_trefle = plants_handler.handle_plant_data(
            "Trefle", trefle_data)
        self.stdout.write(
            self.style.SUCCESS(f"{created_trefle} plant crumbs saved from "
                                "Trefle.")
        )

        permapeople_data = plants.fetch_permapeople_plants()
        created_permapeople = plants_handler.handle_plant_data(
            "PermaPeople", permapeople_data)
        self.stdout.write(
            self.style.SUCCESS(
                f"{created_permapeople} plant crumbs saved from PermaPeople."
            )
        )

        # Fetches and handles environment news
        self.stdout.write("Fetching environment news from NewsData.io...")
        environment_articles = environment.fetch_environment_news()
        created_environment = environment_handler.handle_environment_articles(
            environment_articles
            )
        self.stdout.write(
            self.style.SUCCESS(f"{created_environment} environment crumbs "
                               "saved.")
        )

        total_created = sum([
            created_environment,
        ])

        # Fetches and handles TheNewsAPI Sports news (general sports headlines)
        self.stdout.write("Fetching general sports news from TheNewsAPI...")
        thenewsapi_sports_data = sports.fetch_thenewsapi_sports()
        created_thenewsapi = sports_handler.handle_sports_crumbs(
            thenewsapi_sports_data)
        total_created += created_thenewsapi
        self.stdout.write(
            self.style.SUCCESS(f"{created_thenewsapi} general sports crumbs "
                               "saved from TheNewsAPI.")
        )

        # Fetches and handles NewsData.io Fitness news
        # (fitness trends, guides, gym news)
        self.stdout.write("Fetching fitness news from NewsData.io...")
        newsdata_fitness_data = sports.fetch_newsdata_fitness()
        created_newsdata_fitness = sports_handler.handle_sports_crumbs(
            newsdata_fitness_data)
        total_created += created_newsdata_fitness
        self.stdout.write(
            self.style.SUCCESS(f"{created_newsdata_fitness} fitness crumbs "
                               "saved from NewsData.io.")
        )

        # Fetches and handles Finnhub General News
        self.stdout.write("Fetching general finance news from Finnhub...")
        finnhub_data = finance.fetch_finnhub_general_news()
        created_finance = finance_handler.handle_finance_crumbs(finnhub_data)
        total_created += created_finance
        self.stdout.write(
            self.style.SUCCESS(f"{created_finance} finance crumbs saved from "
                               "Finnhub.")
        )

        # Print the total number of crumbs added
        self.stdout.write(
            self.style.SUCCESS(f" Total crumbs added: {total_created}")
        )