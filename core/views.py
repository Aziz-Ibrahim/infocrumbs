from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.models import Site

from subscriptions.models import UserSubscription
from .forms import ContactForm


# home
def home(request):
    """
    Renders the home page with dynamic call-to-action based on user's
    subscription status.
    """
    user_subscription_status = {
        'is_subscribed': False,
        'is_premium': False,
        'has_active_sub_plan': None # Stores the name of active plan if any
    }

    if request.user.is_authenticated:
        # Get the latest active subscription for the current user
        active_subscription = UserSubscription.objects.filter(
            user=request.user,
            active=True,
            end_date__gte=timezone.now()
        ).order_by('-end_date').first()

        if active_subscription:
            user_subscription_status['is_subscribed'] = True
            user_subscription_status['has_active_sub_plan'] = (
                active_subscription.plan.name
            )

            if active_subscription.plan.name.lower() == 'premium':
                user_subscription_status['is_premium'] = True
    
    context = {
        'user_subscription_status': user_subscription_status,
    }
    return render(request, 'core/home.html', context)


# About
def about(request):
    """
    Renders the About page.
    """
    return render(request, 'core/about.html')


# FAQ
def faq_view(request):
    """
    Renders the Frequently Asked Questions page.
    """
    return render(request, 'core/faq.html')


# Contact
def contact_view(request):
    """
    Handles the contact form submission, sending an email to the site admin.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            user_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            current_site = Site.objects.get_current()
            site_domain = current_site.domain

            context = {
                'name': name,
                'email': user_email,
                'subject': subject,
                'message': message,
                'site_name': 'InfoCrumbs',
                'site_domain': site_domain,
            }

            html_message_body = render_to_string(
                'core/emails/contact_form_email.html', context
            )
            plain_message_body = render_to_string(
                'core/emails/contact_form_email.txt', context
            )

            try:
                email = EmailMultiAlternatives(
                    subject=f"Contact Form: {subject}",
                    body=plain_message_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['infocrumbs.app@gmail.com'],
                    reply_to=[user_email],
                )
                
                email.attach_alternative(html_message_body, "text/html")

                email.send(fail_silently=False)

                messages.success(
                    request,
                    'Your message has been sent successfully!'
                )
                return redirect('contact')
            except Exception as e:
                messages.error(
                    request,
                    'There was an error sending your message. '
                    'Please try again later.'
                )
                print(f"Error sending contact email: {e}")
        else:
            pass
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})