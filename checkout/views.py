import stripe
import json
from datetime import timedelta
from django.shortcuts import (render,
                              redirect,
                              reverse,
                              get_object_or_404,
                              HttpResponse)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.http import require_POST
from django.utils.timezone import now

from subscriptions.models import (SubscriptionPlan,
                                  SubscriptionFrequency,
                                  UserSubscription)
from subscriptions.utils import calculate_subscription_price

# Set Stripe API key globally for the module
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def checkout_subscription(request, plan_id, frequency_id):
    """
    Renders the checkout page for a selected subscription plan and frequency.
    Creates a Stripe PaymentIntent.
    """
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    try:
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        frequency = get_object_or_404(SubscriptionFrequency, id=frequency_id)
    except Exception as e:
        messages.error(request, "The requested subscription plan or frequency was not found.")
        return redirect('choose_plan')

    final_price = calculate_subscription_price(plan.name, frequency.duration_days)

    if final_price is None:
        messages.error(request, "Could not calculate the price for the selected plan. Please try again.")
        return redirect('choose_plan')

    if request.method == 'POST':
        messages.error(request, "Direct POST not expected here. Payment processed via Stripe API.")
        return redirect('choose_plan')
    else:
        if not stripe_public_key:
            messages.warning(request, 'Stripe public key is missing. Did you forget to set it in your environment?')

        stripe_total = round(final_price * 100)

        try:
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY,
                metadata={
                    'plan_id': plan.id,
                    'frequency_id': frequency.id,
                    'username': request.user.username if request.user.is_authenticated else 'AnonymousUser',
                }
            )
            client_secret = intent.client_secret
        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe payment error: {e}")
            return redirect('choose_plan')
        except Exception as e:
            messages.error(request, f"An unexpected error occurred during payment intent creation: {e}")
            return redirect('choose_plan')

        context = {
            'plan': plan,
            'frequency': frequency,
            'price': final_price,
            'stripe_public_key': stripe_public_key,
            'client_secret': client_secret,
            'plan_id': plan.id,
            'frequency_id': frequency.id,
        }
        return render(request, 'checkout/checkout.html', context)


@require_POST
def cache_checkout_data(request):
    """
    AJAX endpoint to cache checkout data in PaymentIntent metadata.
    This view would typically handle AJAX requests from the client
    to update PaymentIntent metadata before payment confirmation.
    For now, it just returns a 200 status.
    """
    return HttpResponse(status=200)

def checkout_success(request, payment_intent_id):
    """
    Renders the success page after a successful payment.
    This view would typically retrieve payment details using payment_intent_id
    and display confirmation to the user.
    """
    return render(
        request, 'checkout/checkout_success.html',
        {'payment_intent_id': payment_intent_id}
        )