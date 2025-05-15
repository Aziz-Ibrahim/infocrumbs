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


# class SubscriptionPlan(models.Model):
#     PLAN_CHOICES = [
#         ('basic', 'Basic'),
#         ('premium', 'Premium'),
#     ]
#     DURATION_CHOICES = [
#         ('weekly', 'Weekly'),
#         ('monthly', 'Monthly'),
#         ('annually', 'Annually'),
#     ]
#     name = models.CharField(max_length=20, choices=PLAN_CHOICES)
#     duration = models.CharField(max_length=20, choices=DURATION_CHOICES)
#     price = models.DecimalField(max_digits=6, decimal_places=2)

#     def __str__(self):
#         return f"{self.name.title()} - {self.duration.title()}"


# class UserSubscription(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
#     subscribed_on = models.DateTimeField(auto_now_add=True)
#     valid_until = models.DateTimeField()

#     def __str__(self):
#         return f"{self.user.username} - {self.plan}"
