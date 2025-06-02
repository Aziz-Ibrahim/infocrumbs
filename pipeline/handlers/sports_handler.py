from datetime import datetime
from crumbs.models import Crumb
from preferences.models import Topic


def save_sports_articles(articles):
    topic = Topic.objects.filter(slug="sports-and-fitness").first()
    if not topic:
        print("Topic 'sports and fitness' not found.")
        return 0

    created_count = 0
    for article in articles:
        if Crumb.objects.filter(
            title=article['title'],
            url=article['url']
            ).exists():
            continue

        try:
            Crumb.objects.create(
                title=article["title"][:255],
                summary=article.get("summary", "")[:500],
                url=article["url"],
                source=article.get("source", "Unknown"),
                topic=topic,
                published_at=datetime.fromisoformat(article["published_at"].replace("Z", "+00:00")),
            )
            created_count += 1
        except Exception as e:
            print(f"Error saving sports article: {e}")
            continue

    return created_count
