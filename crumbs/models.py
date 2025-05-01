from django.db import models
from django.contrib.auth import get_user_model

class Crumb(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('music', 'Music'),
        ('finance', 'Finance'),
        ('quote', 'Quote'),
        ('sports', 'Sports'),
        ('gardening', 'Gardening'),
        ('diy', 'DIY / Crafts'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    source_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.category})"
