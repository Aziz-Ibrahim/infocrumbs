import json
import stripe
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from subscriptions.models import UserSubscription
from django.utils.timezone import now, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from subscriptions.models import SubscriptionPlan, SubscriptionFrequency
from subscriptions.utils import calculate_subscription_price

stripe.api_key = settings.STRIPE_SECRET_KEY
User = get_user_model()

def checkout_view(request):
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    }
    return render(request, 'checkout/checkout.html', context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    # Handle successful payment
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']

        metadata = intent.get('metadata', {})
        user_id = metadata.get('user_id')
        plan_id = metadata.get('plan_id')
        frequency_id = metadata.get('frequency_id')

        try:
            user = User.objects.get(id=user_id)
            plan = SubscriptionPlan.objects.get(id=plan_id)
            frequency = SubscriptionFrequency.objects.get(id=frequency_id)

            expires_at = now() + timedelta(days=frequency.duration_days)

            # Save or update the subscription
            UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'frequency': frequency,
                    'expires_at': expires_at,
                }
            )

            print(f" Subscription saved for user {user.username}")

        except (User.DoesNotExist,
                SubscriptionPlan.DoesNotExist,
                SubscriptionFrequency.DoesNotExist):
            print(" Webhook error: invalid user or subscription data.")

    return HttpResponse(status=200)


@require_POST
@login_required
@csrf_exempt
def create_payment_intent(request):
    try:
        data = json.loads(request.body)
        plan_id = data.get('plan_id')
        frequency_id = data.get('frequency_id')

        plan = SubscriptionPlan.objects.get(id=plan_id)
        frequency = SubscriptionFrequency.objects.get(id=frequency_id)

        # Use the utility function to calculate the final price
        final_price = calculate_subscription_price(plan.name,
                                                   frequency.duration_days)

        if final_price is None:
            return JsonResponse(
                {'error': 'Invalid plan or frequency combination'}, status=400)

        amount = int(final_price * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="gbp",
            metadata={
                "user_id": request.user.id,
                "plan_id": plan_id,
                "frequency_id": frequency_id,
            },
        )

        return JsonResponse({'clientSecret': intent.client_secret})

    except SubscriptionPlan.DoesNotExist:
        return JsonResponse(
            {'error': 'Subscription Plan not found'}, status=404)
    except SubscriptionFrequency.DoesNotExist:
        return JsonResponse(
            {'error': 'Subscription Frequency not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        # Catch other potential errors, e.g., Stripe API errors
        return JsonResponse({'error': str(e)}, status=400)
