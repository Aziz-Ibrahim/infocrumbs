from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.utils.timezone import now as timezone_now

from crumbs.models import Crumb
from preferences.models import Topic
from pipeline.utils import clean_text, summarize_text, tag_crumb_text


def handle_world_news_crumbs(crumb_data_list):
    """
    Handles world news crumbs by creating or updating Crumb objects.
    Each crumb is primarily associated with the 'world-news' topic
    and can receive additional tags based on its content.

    Args:
        crumb_data_list (list): List of dictionaries containing crumb data.

    Returns:
        int: Number of Crumb objects created.
    """
    world_news_slug = "world-news"
    try:
        world_news_topic = Topic.objects.get(slug=world_news_slug)
    except Topic.DoesNotExist:
        # Create the topic if it doesn't exist
        world_news_topic = Topic.objects.create(
            name="world news",
            slug=world_news_slug
        )

    created_count = 0
    for item in crumb_data_list:
        title = item.get("title", "")[:255]
        url = item.get("url")
        raw_summary = item.get("summary") or item.get("description", "")

        if not title or not url:
            print(f"Skipping world news crumb due to missing title or URL: "
                  f"{item}")
            continue

        if Crumb.objects.filter(title=title, url=url).exists():
            continue

        try:
            # Clean the raw summary/description text
            cleaned_content = clean_text(raw_summary)

            # Summarize the cleaned text
            final_summary = summarize_text(cleaned_content) if \
                cleaned_content else ""

            # Handle published_at: parse if string, make timezone-aware,
            # else use now()
            published_at = None
            pub_date_str = item.get("published_at")
            if pub_date_str:
                parsed_dt = parse_datetime(pub_date_str)
                if parsed_dt:
                    if timezone.is_naive(parsed_dt):
                        published_at = timezone.make_aware(
                            parsed_dt, timezone.get_current_timezone())
                    else:
                        published_at = parsed_dt

            if published_at is None:
                published_at = timezone_now()

            crumb = Crumb.objects.create(
                title=title,
                summary=final_summary,
                url=url,
                source=item.get("source", "Unknown"),
                topic=world_news_topic,
                published_at=published_at,
            )
            created_count += 1

            # Use tag_crumb_text to find additional tags
            text_for_tagging = f"{title} {cleaned_content}"
            matched_topic_for_tag = tag_crumb_text(text_for_tagging)

            if matched_topic_for_tag and \
               matched_topic_for_tag != world_news_topic:
                crumb.tags.add(matched_topic_for_tag.name)

        except Exception as e:
            print(f"Error saving world news crumb (Title: "
                  f"{title[:50]}...): {e}")
            continue

    return created_count
