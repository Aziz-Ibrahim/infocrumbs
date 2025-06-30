from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site


def send_security_alert_email(user, change_type, ip_address=None):
    """
    Sends a security alert email to the user.
    """
    subject = 'Important: Your InfoCrumbs Account Activity'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]

    current_site = Site.objects.get_current()
    site_domain = current_site.domain

    context = {
        'user': user,
        'change_type': change_type,
        'ip_address': ip_address if ip_address else 'Unknown',
        'login_history_url': f"{settings.SITE_URL}{reverse('account_login')}",
        'site_name': 'InfoCrumbs',
        'site_domain': site_domain,
    }

    html_content = render_to_string(
        'emails/security_alert.html', context
    )
    text_content = render_to_string(
        'emails/security_alert.txt', context
    )

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        recipient_list
        )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
