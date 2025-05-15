from django.db import models
from django.conf import settings


class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    topics = models.ManyToManyField(Topic)

    def __str__(self):
        return f"{self.user.username}'s preferences"
    
