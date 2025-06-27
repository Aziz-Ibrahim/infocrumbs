from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from subscriptions.models import UserSubscription, SubscriptionPlan
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

            # Construct the email body
            email_body = (
                f"Name: {name}\n"
                f"Email: {user_email}\n"
                f"Subject: {subject}\n\n"
                f"Message:\n{message}"
            )

            try:
                send_mail(
                    subject=f"Contact Form: {subject}",
                    message=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['infocrumbs.app@gmail.com'],
                    fail_silently=False,
                )
                messages.success(
                    request, 'Your message has been sent successfully!'
                )
                return redirect('contact')
            except Exception as e:
                messages.error(
                    request,
                    'There was an error sending your message. Please '
                    'try again later.'
                )
                print(f"Error sending contact email: {e}")  # debugging
        else:
            pass
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})