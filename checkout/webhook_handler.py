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

        # Extract metadata for subscription details
        plan_id = intent.metadata.plan_id
        frequency_id = intent.metadata.frequency_id
        username = intent.metadata.username

        # Retrieve related Django objects
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            frequency = SubscriptionFrequency.objects.get(id=frequency_id)
        except (
            SubscriptionPlan.DoesNotExist, SubscriptionFrequency.DoesNotExist
        ):
            print(
                f"Webhook Error: Plan (ID: {plan_id}) or Frequency (ID: "
                f"{frequency_id}) not found for PaymentIntent {pid}."
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
            except User.DoesNotExist:
                print(
                    f"Webhook Error: User '{username}' not found for "
                    f"PaymentIntent {pid}."
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

        start_date = now()
        end_date = start_date + timedelta(days=frequency.duration_days)

        user_subscription_exists = False
        try:
            user_subscription = UserSubscription.objects.get(
                stripe_payment_intent_id=pid
            )
            user_subscription_exists = True
            if not user_subscription.active or \
               user_subscription.plan != plan or \
               user_subscription.frequency != frequency or \
               user_subscription.end_date < end_date:
                user_subscription.active = True
                user_subscription.plan = plan
                user_subscription.frequency = frequency
                user_subscription.start_date = start_date
                user_subscription.end_date = end_date
                user_subscription.save()
            print(
                f"Webhook Success: PaymentIntent {pid} already processed. "
                f"UserSubscription updated/verified."
            )

            send_subscription_confirmation_email(user, user_subscription)
            print(
                f"Sent confirmation email to {user.email} for subscription "
                f"ID {user_subscription.pk}"
            )

            return HttpResponse(
                content=(
                    f'Webhook received: {event["type"]} | SUCCESS: '
                    f'Verified subscription already in database for PI: {pid}'
                ),
                status=200
            )
        except UserSubscription.DoesNotExist:
            pass

        try:
            user_subscription = UserSubscription.objects.get(user=user)
            user_subscription.plan = plan
            user_subscription.frequency = frequency
            user_subscription.start_date = start_date
            user_subscription.end_date = end_date
            user_subscription.active = True
            user_subscription.stripe_payment_intent_id = pid
            user_subscription.save()
            message_content = (
                f'SUCCESS: Existing user subscription updated for PI: {pid}.'
            )
            print(
                f"Webhook Success: User {user.username}'s existing "
                f"subscription updated for PI: {pid}."
            )

            send_subscription_confirmation_email(user, user_subscription)
            print(
                f"Sent confirmation email to {user.email} for subscription "
                f"ID {user_subscription.pk}"
            )

        except UserSubscription.DoesNotExist:
            # No existing subscription for the user, create a new one.
            try:
                user_subscription = UserSubscription.objects.create(
                    user=user,
                    plan=plan,
                    frequency=frequency,
                    start_date=start_date,
                    end_date=end_date,
                    active=True,
                    stripe_payment_intent_id=pid,
                )
                message_content = (
                    f'SUCCESS: New user subscription created for PI: {pid}.'
                )
                print(
                    f"Webhook Success: New user subscription created for "
                    f"{user.username} for PI: {pid}."
                )

                send_subscription_confirmation_email(user, user_subscription)
                print(
                    f"Sent confirmation email to {user.email} for subscription "
                    f"ID {user_subscription.pk}"
                )

            except Exception as e:
                print(
                    f"Webhook Error: Failed to create new subscription for "
                    f"user {user.username} for PI {pid}: {e}"
                )
                return HttpResponse(
                    content=(
                        f'Webhook received: {event["type"]} | ERROR creating '
                        f'new subscription: {e}. PI: {pid}'
                    ),
                    status=500
                )

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | {message_content}',
            status=200,
        )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe.
        Optionally deactivate the user's subscription if the payment failed.
        """
        intent = event.data.object
        pid = intent.id
        username = intent.metadata.username

        print(f"Payment failed for PaymentIntent {pid}. User: {username}")

        if username and username != 'AnonymousUser':
            try:
                user = User.objects.get(username=username)
                user_subscription = UserSubscription.objects.get(user=user)
                user_subscription.active = False
                user_subscription.save()
                print(
                    f"User {username}'s subscription marked inactive due to "
                    f"failed payment for PI: {pid}."
                )
            except User.DoesNotExist:
                print(
                    f"Webhook Info: User {username} not found for failed "
                    f"payment webhook for PI: {pid}."
                )
            except UserSubscription.DoesNotExist:
                print(
                    f"Webhook Info: No subscription found for user {username} "
                    f"to deactivate for PI: {pid}."
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
