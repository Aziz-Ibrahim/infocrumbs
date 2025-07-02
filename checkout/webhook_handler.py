import json
import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from datetime import timedelta

from subscriptions.email import send_subscription_confirmation_email
from subscriptions.models import (
    SubscriptionPlan,
    SubscriptionFrequency,
    UserSubscription
)

User = get_user_model()


class StripeWH_Handler:
    """Handle Stripe webhooks for subscriptions"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe.
        This is where the UserSubscription is created or updated.
        """
        intent = event.data.object
        pid = intent.id  # Stripe Payment Intent ID

        plan_id = intent.metadata.get('plan_id')
        frequency_id = intent.metadata.get('frequency_id')
        username = intent.metadata.get('username')
        final_price = intent.amount / 100  # Stripe amount is in cents

        # Retrieve related Django objects
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            frequency = SubscriptionFrequency.objects.get(id=frequency_id)
        except (
            SubscriptionPlan.DoesNotExist, SubscriptionFrequency.DoesNotExist
        ) as e:
            print(
                f"Webhook Error: Plan (ID: {plan_id}) or Frequency (ID: "
                f"{frequency_id}) not found for PaymentIntent "
                f"{pid}. Error: {e}"
            )
            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]} | ERROR: Plan '
                    f'or Frequency not found for PI: {pid}'
                ),
                status=400
            )

        user = None
        if username and username != 'AnonymousUser':
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist as e:
                print(
                    f"Webhook Error: User '{username}' not found for "
                    f"PaymentIntent {pid}. Error: {e}"
                )
                return HttpResponse(
                    content=(
                        f'Webhook received: {event["type"]} | ERROR: '
                        f'User not found for PI: {pid}'
                    ),
                    status=400
                )
        else:
            print(
                f"Webhook Error: Anonymous user payment intent received "
                f"for PI {pid}. This flow requires a logged-in user."
            )
            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]} | ERROR: '
                    f'Anonymous user cannot subscribe via this flow '
                    f'for PI: {pid}'
                ),
                status=400
            )

        try:
            subscription, created = UserSubscription.objects.update_or_create(
                stripe_payment_intent_id=pid,  # Use PID as the unique lookup
                defaults={
                    'user': user,
                    'plan': plan,
                    'frequency': frequency,
                    'active': True,  # Mark as active
                }
            )

            # Update user's premium status and subscription type
            user.is_premium = (plan.name == 'premium')
            user.subscription_type = frequency.name
            user.save()

            # Send confirmation email with the final price
            send_subscription_confirmation_email(
                user,
                subscription,
                final_price
            )

            if created:
                message_content = (
                    f'SUCCESS: New user subscription created for PI: {pid}.'
                )
                print(
                    f"Webhook Success: New user subscription created for "
                    f"{user.username} for PI: {pid}."
                )
            else:
                message_content = (
                    f'SUCCESS: Existing user subscription updated/verified '
                    f'for PI: {pid}.'
                )
                print(
                    f"Webhook Success: User {user.username}'s subscription "
                    f"updated/verified for PI: {pid}."
                )

            print(
                f"Sent confirmation email to {user.email} for subscription "
                f"ID {subscription.pk}"
            )

            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]} | {message_content}'
                ),
                status=200
            )

        except Exception as e:
            print(
                f"Webhook Error: Failed to create/update subscription for "
                f"user {user.username} for PI {pid}: {e}"
            )
            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]} | '
                    f'ERROR creating/updating subscription: {e}. PI: {pid}'
                ),
                status=500
            )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe.
        Optionally deactivate the user's subscription if the payment failed.
        """
        intent = event.data.object
        pid = intent.id
        username = intent.metadata.get('username') # Use .get() for safety

        print(f"Payment failed for PaymentIntent {pid}. User: {username}")

        if username and username != 'AnonymousUser':
            try:
                user = User.objects.get(username=username)
                # Try to find the specific subscription by PI ID if possible,
                # otherwise by user.
                user_subscription = UserSubscription.objects.get(
                    stripe_payment_intent_id=pid, user=user
                )
                user_subscription.active = False
                user_subscription.save()
                print(
                    f"User {username}'s subscription (PI: {pid}) marked "
                    f"inactive due to failed payment."
                )
            except User.DoesNotExist:
                print(
                    f"Webhook Info: User {username} not found for failed "
                    f"payment webhook for PI: {pid}."
                )
            except UserSubscription.DoesNotExist:
                print(
                    f"Webhook Info: No matching subscription found for user "
                    f"{username} and PI {pid} to deactivate."
                )
            except Exception as e:
                print(
                    f"Webhook Error: Error attempting to deactivate "
                    f"subscription for user {username} for PI {pid}: {e}"
                )

        return HttpResponse(
            content=(
                f'Webhook received: {event["type"]} | Payment failed for '
                f'PaymentIntent {pid}.'
            ),
            status=200
        )
