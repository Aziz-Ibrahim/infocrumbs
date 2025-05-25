from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from crumbs.models import Crumb
from feedback.models import Comment
from preferences.models import Topic


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_premium = models.BooleanField(default=False)
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('annually', 'Annually'),
        ],
        default='none',
    )

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    saved_crumbs = models.ManyToManyField(Crumb, blank=True)
    comment_history = models.ManyToManyField(Comment, blank=True)
    topic_preferences = models.ManyToManyField(Topic, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"