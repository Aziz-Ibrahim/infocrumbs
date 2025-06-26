from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    """
    Represents a subscription plan with different options.
    """
    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
    ]
    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    topic_limit = models.PositiveIntegerField(default=2)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return self.get_name_display()


class SubscriptionFrequency(models.Model):
    """
    Represents the frequency of subscription billing.
    """
    name = models.CharField(max_length=20, unique=True)
    duration_days = models.PositiveIntegerField()
    discount_percent = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.discount_percent}% off)"


class UserSubscription(models.Model):
    """
    Represents a user's subscription to a plan with a specific frequency.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
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
    start_date = models.DateTimeField(blank=True)
    end_date = models.DateTimeField(blank=True)
    active = models.BooleanField(default=False)
    stripe_payment_intent_id = models.CharField(
        max_length=255, blank=True, null=True, unique=True
    )
    last_reminder_sent = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Automatically sets start and end dates based on the latest
        existing subscription of the same user.
        """
        duration = timedelta(days=self.frequency.duration_days)

        # Get latest active or future-dated sub
        latest_sub = UserSubscription.objects.filter(
            user=self.user,
            end_date__gte=timezone.now()
        ).order_by('-end_date').first()

        if not self.start_date or not self.end_date:
            if latest_sub and latest_sub.plan == self.plan and \
                    latest_sub.frequency == self.frequency:
                # Extend current sub
                self.start_date = latest_sub.end_date
            else:
                self.start_date = latest_sub.end_date if (
                    latest_sub
                ) else timezone.now()

            self.end_date = self.start_date + duration

        super().save(*args, **kwargs)

    def is_active(self):
        return self.active and self.end_date > timezone.now()

    def _str_(self):
        return f"{self.user.username} - {self.plan.name} ({self.frequency})"