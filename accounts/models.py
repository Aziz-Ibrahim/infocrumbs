from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from crumbs.models import Crumb
from feedback.models import Comment
from preferences.models import Topic


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Includes additional fields for user profile information,
    subscription status, and email verification.
    """
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
    date_of_birth = models.DateField(null=True, blank=True)
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        """
        Returns the username as the string representation of the user.
        """
        return self.username


class Profile(models.Model):
    """
    Profile model associated with CustomUser.
    Stores user-specific data like saved crumbs, comment history,
    and topic preferences.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    saved_crumbs = models.ManyToManyField(Crumb, blank=True)
    comment_history = models.ManyToManyField(Comment, blank=True)
    topic_preferences = models.ManyToManyField(Topic, blank=True)

    def __str__(self):
        """
        Returns a string representation of the user's profile.
        """
        return f"{self.user.username}'s Profile"
