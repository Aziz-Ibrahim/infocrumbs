from preferences.models import Topic
from django.utils.text import slugify
from django.utils.timezone import now

from crumbs.models import Crumb
from pipeline.utils import summarize_text


def handle_foodcrumbs(recipes):
    """
    Save random recipes as 'food and drinks' crumbs.
    """
    topic, _ = Topic.objects.get_or_create(name="food and drink", defaults={
        "slug": slugify("food and drink")
    })

    created_count = 0
    for recipe in recipes:
        title = recipe.get("title", "").strip()
        url = recipe.get("sourceUrl")

        if not title or not url or \
            Crumb.objects.filter(title=title, url=url).exists():
                continue

        summary = recipe.get("summary") or recipe.get("instructions", "")
        summarized = summarize_text(summary)

        try:
            Crumb.objects.create(
                title=title[:255],
                summary=summarized,
                url=url,
                source="Spoonacular",
                topic=topic,
                published_at=now()
            )
            created_count += 1
        except Exception as e:
            print(f"Error saving food crumb: {e}")
            continue

    return created_count
