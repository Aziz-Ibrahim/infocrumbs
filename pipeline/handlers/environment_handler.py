# pipeline/handlers/environment_handler.py

from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.utils.timezone import now as timezone_now # Renamed to avoid confusion with datetime.now
from django.utils import timezone # Import timezone module for make_aware, is_naive

from crumbs.models import Crumb
from preferences.models import Topic
from pipeline.utils import summarize_text, clean_text, tag_crumb_text


def handle_environment_articles(articles):
    """
    Handles environment-related articles by creating or updating Crumb objects.
    Each crumb is primarily associated with the 'environment' topic and can
    receive additional tags based on its content.

    :param articles: List of dictionaries containing article data from NewsData.io.
    :return: Number of Crumb objects created.
    """
    environment_slug = "environment"
    try:
        environment_topic = Topic.objects.get(slug=environment_slug)
    except Topic.DoesNotExist:
        # Create the topic if it doesn't exist
        environment_topic = Topic.objects.create(
            name="Environment",
            slug=environment_slug
        )

    created_count = 0
    for article in articles:
        title = article.get("title", "")[:255]
        url = article.get("link")
        raw_description = article.get("description", "")

        if not title or not url:
            print(f"Skipping environment article due to missing title or URL: {article}")
            continue

        if Crumb.objects.filter(title=title, url=url).exists():
            continue

        try:
            cleaned_content = clean_text(raw_description)
            final_summary = summarize_text(cleaned_content) if cleaned_content else ""

            # --- FIX for Naive DateTime Warning ---
            pub_date_str = article.get("pubDate")
            published_at = None
            if pub_date_str:
                parsed_dt = parse_datetime(pub_date_str)
                if parsed_dt: # Check if parsing was successful
                    if timezone.is_naive(parsed_dt):
                        # Make it timezone-aware using the default timezone
                        published_at = timezone.make_aware(parsed_dt, timezone.get_current_timezone())
                    else:
                        published_at = parsed_dt
            
            # Fallback to timezone-aware now() if published_at is still None
            if published_at is None:
                published_at = timezone_now()
            # --- END FIX ---

            crumb = Crumb.objects.create(
                title=title,
                summary=final_summary,
                url=url,
                source=article.get("source_id", "NewsData.io"),
                topic=environment_topic,
                published_at=published_at, # Use the now timezone-aware datetime
            )
            created_count += 1

            text_for_tagging = f"{title} {cleaned_content}"
            matched_topic_for_tag = tag_crumb_text(text_for_tagging)
            
            if matched_topic_for_tag and matched_topic_for_tag != environment_topic:
                crumb.tags.add(matched_topic_for_tag.name)

        except Exception as e:
            print(f"Error saving environment article (Title: {title[:50]}...): {e}")
            continue

    return created_count