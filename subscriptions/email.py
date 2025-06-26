from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from .models import UserSubscription


def send_subscription_confirmation_email(user, subscription):
    """
    Sends a subscription confirmation email to the user.

    Args:
        user (CustomUser): The user object to whom the email will be sent.
        subscription (UserSubscription): The subscription object containing
        details.
    """
    subject = 'InfoCrumbs Subscription Confirmation!'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    # Context for the email templates
    context = {
        'user': user,
        'subscription': subscription,
        'profile_url': f"{settings.SITE_URL}{reverse('account_profile')}",
        'site_name': 'InfoCrumbs',
    }

    # Render HTML and plain text versions
    html_content = render_to_string(
        'subscriptions/email/subscription_confirmation.html', context
    )
    text_content = render_to_string(
        'subscriptions/email/subscription_confirmation.txt', context
    )

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        recipient_list
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_subscription_expiry_reminders():
    """
    Sends email reminders to users whose subscriptions expire in 24-48 hours.
    """
    now = timezone.now()
    twenty_four = now + timedelta(hours=24)
    forty_eight = now + timedelta(hours=48)

    expiring_subs = UserSubscription.objects.filter(
        active=True,
        end_date__gte=twenty_four,
        end_date__lt=forty_eight
    ).select_related('user')

    print(f"Found {expiring_subs.count()} subscriptions expiring soon.")

    for sub in expiring_subs:
        user = sub.user

        # Skip if user already has a queued subscription
        has_queued_sub = UserSubscription.objects.filter(
            user=user,
            active=False,
            start_date__gt=sub.end_date
        ).exists()
        if has_queued_sub:
            continue

        # Skip if reminder already sent in last 24h
        if (
            sub.last_reminder_sent and
            timezone.now() - sub.last_reminder_sent < timedelta(hours=24)
        ):
            continue

        context = {
            'user': user,
            'subscription': sub,
            'profile_url': f"{settings.SITE_URL}{reverse('account_profile')}",
            'choose_plan_url': f"{settings.SITE_URL}{reverse('choose_plan')}",
            'site_name': 'InfoCrumbs',
        }

        subject = "Your InfoCrumbs Subscription Expires Soon!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        html_content = render_to_string(
            'subscriptions/email/subscription_reminder.html',
            context
        )
        text_content = render_to_string(
            'subscriptions/email/subscription_reminder.txt',
            context
        )

        msg = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            recipient_list
        )
        msg.attach_alternative(html_content, "text/html")

        try:
            msg.send()
            sub.last_reminder_sent = timezone.now()
            sub.save(update_fields=['last_reminder_sent'])
            print(f"Reminder sent to {user.email}")
        except Exception as e:
            print(f"Failed to send reminder to {user.email}: {e}")


