from django.core.management.base import BaseCommand

from pipeline.tasks import (
    plants,
    environment,
    sports,
    finance,
    news,
    music,
    technology,
    food,
    trivia,
    )
from pipeline.handlers import (
    plants_handler,
    environment_handler,
    sports_handler,
    finance_handler,
    news_handler,
    music_handler,
    technology_handler,
    food_handler,
    trivia_handler,
    )

class Command(BaseCommand):
    help = 'Fetches crumbs from various sources and adds them to the database.'

    def handle(self, *args, **options):
        self.stdout.write("Starting crumb fetching process...")
        total_created = 0

        # Fetches and handles plnats and gardening crumbs from 3 APIs
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

        # Fetches and handles NewsData.io World News
        self.stdout.write("Fetching general world news from NewsData.io...")
        newsdata_world_news_data = news.fetch_newsdata_world_news()
        created_newsdata_world_news = news_handler.handle_world_news_crumbs(
            newsdata_world_news_data)
        total_created += created_newsdata_world_news
        self.stdout.write(
            self.style.SUCCESS(f"{created_newsdata_world_news} world news "
                               "crumbs saved from NewsData.io.")
        )

        # Fetches and handles NewsAPI.org World News
        self.stdout.write(
            "Fetching world news from NewsAPI.org (UK headlines)...")
        newsapi_world_news_data = news.fetch_newsapi_world_news()
        created_newsapi_world_news = news_handler.handle_world_news_crumbs(
            newsapi_world_news_data)
        total_created += created_newsapi_world_news
        self.stdout.write(
            self.style.SUCCESS(f"{created_newsapi_world_news} world news "
                               "crumbs saved from NewsAPI.org.")
        )

        # Fetches and handles Last.fm Artist Bios
        self.stdout.write("Fetching artist bios from Last.fm...")
        lastfm_artist_data = music.fetch_lastfm_top_artists_bios()
        created_lastfm_artists = music_handler.handle_music_crumbs(
            lastfm_artist_data)
        total_created += created_lastfm_artists
        self.stdout.write(
            self.style.SUCCESS(f"{created_lastfm_artists} music (artist bio) "
                               "crumbs saved from Last.fm.")
        )

        # Fetches and handles NewsData.io Music News
        self.stdout.write("Fetching music news from NewsData.io...")
        newsdata_music_data = music.fetch_newsdata_music_news()
        created_newsdata_music = music_handler.handle_music_crumbs(
            newsdata_music_data)
        total_created += created_newsdata_music
        self.stdout.write(
            self.style.SUCCESS(f"{created_newsdata_music} music news crumbs "
                               "saved from NewsData.io.")
        )

        # Fetches and handles Mediastack Technology News
        self.stdout.write("Fetching technology news from Mediastack...")
        mediastack_tech_data = technology.fetch_mediastack_technology_news()
        created_tech = technology_handler.handle_technology_crumbs(
            mediastack_tech_data)
        total_created += created_tech
        self.stdout.write(
            self.style.SUCCESS(f"{created_tech} technology crumbs saved from "
                               "Mediastack.")
        )

        # Fetches and handles Spoonacular random recipes
        self.stdout.write("Fetching random recipes from Spoonacular...")
        spoonacular_data = food.fetch_spoonacular_random_recipes()
        created_spoonacular = food_handler.handle_food_drink_crumbs(
            spoonacular_data
            )
        total_created += created_spoonacular
        self.stdout.write(
            self.style.SUCCESS(f"{created_spoonacular} food & drink (recipe) "
                               "crumbs saved from Spoonacular.")
        )

        # Fetches and handles NewsData.io Food & Drink News
        self.stdout.write("Fetching food & drink news from NewsData.io...")
        newsdata_food_drink_data = food.fetch_newsdata_food_drink_news()
        created_newsdata_food_drink = food_handler.handle_food_drink_crumbs(
            newsdata_food_drink_data)
        total_created += created_newsdata_food_drink
        self.stdout.write(
            self.style.SUCCESS(f"{created_newsdata_food_drink} food & drink "
                               "news crumbs saved from NewsData.io.")
        )

        # Fetches and handles Useless Facts
        self.stdout.write("Fetching useless facts...")
        useless_facts_data = trivia.fetch_useless_facts()
        created_useless_facts = trivia_handler.handle_trivia_fun_crumbs(
            useless_facts_data)
        total_created += created_useless_facts
        self.stdout.write(
            self.style.SUCCESS(f"{created_useless_facts} useless fact crumbs "
                               "saved.")
        )

        # Fetches and handles Chuck Norris Jokes
        self.stdout.write("Fetching Chuck Norris jokes...")
        chuck_norris_data = trivia.fetch_chuck_norris_jokes()
        created_chuck_norris = trivia_handler.handle_trivia_fun_crumbs(
            chuck_norris_data)
        total_created += created_chuck_norris
        self.stdout.write(
            self.style.SUCCESS(f"{created_chuck_norris} Chuck Norris joke "
                               "crumbs saved.")
        )

        # Fetches and handles Open Trivia questions
        self.stdout.write("Fetching trivia questions from Open Trivia DB...")
        open_trivia_data = trivia.fetch_open_trivia()
        created_open_trivia = trivia_handler.handle_trivia_fun_crumbs(
            open_trivia_data)
        total_created += created_open_trivia
        self.stdout.write(
            self.style.SUCCESS(f"{created_open_trivia} Open Trivia question "
                               "crumbs saved.")
        )

        # Print the total number of crumbs added
        self.stdout.write(
            self.style.SUCCESS(f" Total crumbs added: {total_created}")
        )