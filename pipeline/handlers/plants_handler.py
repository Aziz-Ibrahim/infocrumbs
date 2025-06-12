from django.utils.dateparse import parse_datetime
from django.utils.text import slugify
from django.utils.timezone import now

from crumbs.models import Crumb
from preferences.models import Topic
from pipeline.utils import summarize_text, clean_text, tag_crumb_text


def handle_plant_data(source, data_list):
    """
    Handles plants and gardening crumbs by creating or updating Crumb objects
    based on the provided crumb data list. Each crumb is primarily associated
    with the 'plants-and-gardening' topic and can receive additional tags
    based on its content.

    :param source: The original source name (e.g., "Perenual", "Trefle").
    :param data_list: List of dictionaries containing crumb data from a fetcher.
    :return: Number of Crumb objects created.
    """
    # Ensure the primary 'plants-and-gardening' topic exists
    plants_slug = "plants-and-gardening"
    try:
        plant_topic = Topic.objects.get(slug=plants_slug)
    except Topic.DoesNotExist:
        plant_topic = Topic.objects.create(
            name="plants and gardening",
            slug=plants_slug
        )

    created_count = 0
    for item in data_list:
        # Basic validation for essential fields
        if not item.get("title") or not item.get("url"):
            print(f"Skipping crumb from {source} due to missing title or URL.")
            continue

        # Check for existing crumb by title and URL to prevent duplicates
        if Crumb.objects.filter(title=item["title"], url=item["url"]).exists():
            continue

        try:
            # 1. Get raw summary/description
            raw_summary = item.get("summary") or item.get("description", "")
            
            # 2. Clean the raw summary text
            cleaned_content = clean_text(raw_summary)
            
            # 3. Summarize the cleaned text
            # Ensure text is not empty before summarizing to avoid API errors
            final_summary = summarize_text(
                cleaned_content
            ) if cleaned_content else ""

            # Determine published_at; default to now() if not provided by API
            published_at = parse_datetime(
                item["published_at"]
                ) if item.get("published_at") else now()

            crumb = Crumb.objects.create(
                title=item["title"][:255],  # Truncate title to max_length
                summary=final_summary,
                url=item["url"],
                source=item.get("source", source),
                topic=plant_topic, # Assign the primary topic for plants
                published_at=published_at
            )
            created_count += 1

            # 4. Use tag_crumb_text to find additional tags
            # Combine title and relevant content for comprehensive tagging
            text_for_tagging = f"{item['title']} {cleaned_content}"
            matched_topic_for_tag = tag_crumb_text(text_for_tagging)
            
            # If tag_crumb_text returns a Topic object and it's not the primary topic,
            # add its name as an additional tag.
            if matched_topic_for_tag and matched_topic_for_tag != plant_topic:
                crumb.tags.add(matched_topic_for_tag.name)

        except Exception as e:
            print(f"Error saving plant crumb from {source} "
                  f"(Title: {item.get('title')[:50]}...): {e}")
            continue

    return created_count
