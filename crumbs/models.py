from django.db import models

from preferences.models import Topic


class Crumb(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField()
    url = models.URLField()
    source = models.CharField(max_length=255)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    published_at = models.DateTimeField()
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

