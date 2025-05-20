from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db import models


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


