from django.db import models
from django.conf import settings


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    topic_limit = models.PositiveIntegerField(default=2)

    def __str__(self):
        return self.get_name_display()


class SubscriptionFrequency(models.Model):
    name = models.CharField(max_length=20, unique=True)
    duration_days = models.PositiveIntegerField()
    discount_percent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.discount_percent}% off)"


class UserSubscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.SET_NULL,
        null=True
    )
    frequency = models.ForeignKey(
        SubscriptionFrequency,
        on_delete=models.SET_NULL,
        null=True
    )
    start_date = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

    def is_active(self):
        from django.utils import timezone
        return self.expires_at > timezone.now()

