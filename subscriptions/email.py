from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib.sites.models import Site

from .models import UserSubscription


def send_subscription_confirmation_email(user, subscription):
    """
    Sends a subscription confirmation email to the user.
    """
    subject = 'InfoCrumbs Subscription Confirmation!'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    current_site = Site.objects.get_current()
    site_domain = current_site.domain

    context = {
        'user': user,
        'subscription': subscription,
        'profile_url': f"{settings.SITE_URL}{reverse('account_profile')}",
        'site_name': 'InfoCrumbs',
        'site_domain': site_domain,
    }

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
    Sends 24-hour subscription expiry reminders to users.
    """
    now = timezone.now()
    twenty_four_hours_from_now = now + timedelta(hours=24)
    twenty_five_hours_from_now = now + timedelta(hours=25)

    expiring_subscriptions_candidates = UserSubscription.objects.filter(
        active=True,
        end_date__gte=twenty_four_hours_from_now,
        end_date__lt=twenty_five_hours_from_now,
    ).select_related('user').order_by('end_date')

    print(
        f"DEBUG: Found {expiring_subscriptions_candidates.count()} "
        "subscription candidates for reminder processing."
    )

    current_site = Site.objects.get_current()
    site_domain = current_site.domain

    for subscription_candidate in expiring_subscriptions_candidates:
        user = subscription_candidate.user

        has_newer_active_subscription = UserSubscription.objects.filter(
            user=user,
            active=True,
            end_date__gt=subscription_candidate.end_date
        ).exclude(pk=subscription_candidate.pk).exists()

        if has_newer_active_subscription:
            print(
                f"DEBUG: Skipping reminder for {user.email} (Subscription ID: "
                f"{subscription_candidate.pk}). "
                "Newer active subscription found."
            )
            continue

        subject = 'Your InfoCrumbs Subscription Expires Soon!'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]

        context = {
            'user': user,
            'subscription': subscription_candidate,
            'profile_url': f"{settings.SITE_URL}{reverse('account_profile')}",
            'choose_plan_url': f"{settings.SITE_URL}{reverse('choose_plan')}",
            'site_name': 'InfoCrumbs',
            'site_domain': site_domain,
        }

        html_content = render_to_string(
            'subscriptions/email/subscription_reminder.html', context
        )
        text_content = render_to_string(
            'subscriptions/email/subscription_reminder.txt', context
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
            print(
                f'DEBUG: Successfully sent reminder to {user.email} '
                f'for subscription ending {subscription_candidate.end_date}.'
            )
        except Exception as e:
            print(
                f'ERROR: Failed to send reminder to {user.email}: {e}'
            )

    print('DEBUG: Subscription expiry reminders sending process completed.')
