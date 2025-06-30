from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Topic(models.Model):
    """
    Model representing a topic that users can subscribe to.
    Each topic has a name, a slug for URL purposes, a description, and 
    an image.
    The slug is automatically generated from the name and is unique.
    If a slug already exists, it appends a number to make it unique.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            original_slug = self.slug
            counter = 1
            while Topic.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class UserPreference(models.Model):
    """
    Model representing user preferences for topics.
    Each user can have multiple topics they are interested in.
    The user is linked to the Django user model.
    The topics are stored as a many-to-many relationship.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
        )
    topics = models.ManyToManyField(Topic)

    def __str__(self):
        return f"{self.user.username}'s preferences"
