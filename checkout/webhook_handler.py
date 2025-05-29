# checkout/webhook_handler.py
from django.http import HttpResponse
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
import time

# Import models from the subscriptions app
from subscriptions.models import SubscriptionPlan, SubscriptionFrequency, UserSubscription
from django.contrib.auth import get_user_model

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
        except (SubscriptionPlan.DoesNotExist, SubscriptionFrequency.DoesNotExist):
            # Log this error, as it indicates a mismatch between Stripe metadata and Django data
            print(f"Webhook Error: Plan (ID: {plan_id}) or Frequency (ID: {frequency_id}) not found for PaymentIntent {pid}.")
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: Plan or Frequency not found for PI: {pid}',
                status=400 # Return 400 to tell Stripe to retry
            )

        # Get the user associated with the payment
        user = None
        if username and username != 'AnonymousUser':
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                print(f"Webhook Error: User '{username}' not found for PaymentIntent {pid}.")
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: User not found for PI: {pid}',
                    status=400 # Return 400 to tell Stripe to retry
                )
        else:
            # This flow expects an authenticated user
            print(f"Webhook Error: Anonymous user payment intent received for PI {pid}. This flow requires a logged-in user.")
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: Anonymous user cannot subscribe via this flow for PI: {pid}',
                status=400
            )

        # Calculate the subscription end date
        start_date = now()
        end_date = start_date + timedelta(days=frequency.duration_days)

        # Check for existing UserSubscription linked to this PaymentIntent ID (idempotency)
        # This is crucial to prevent duplicate subscriptions if the webhook is sent multiple times.
        user_subscription_exists = False
        try:
            user_subscription = UserSubscription.objects.get(stripe_payment_intent_id=pid)
            user_subscription_exists = True
            # If it exists, it means this webhook has already been processed for this PI.
            # Just ensure it's active and updated correctly in case of retries/minor inconsistencies.
            if not user_subscription.active or \
               user_subscription.plan != plan or \
               user_subscription.frequency != frequency or \
               user_subscription.end_date < end_date: # Update end date if it's a renewal extending current
                user_subscription.active = True
                user_subscription.plan = plan
                user_subscription.frequency = frequency
                user_subscription.start_date = start_date # Set to now for this payment
                user_subscription.end_date = end_date
                user_subscription.save()
            print(f"Webhook Success: PaymentIntent {pid} already processed. UserSubscription updated/verified.")
            return HttpResponse(
                content=(f'Webhook received: {event["type"]} | SUCCESS: '
                         f'Verified subscription already in database for PI: {pid}'),
                status=200
            )
        except UserSubscription.DoesNotExist:
            pass # Continue to create/update if not found by PI ID

        # If not found by PI ID, check if the user already has an active subscription.
        # If so, update it (e.g., for renewals or plan changes).
        # Assuming UserSubscription is a OneToOneField, a user only has one at a time.
        try:
            user_subscription = UserSubscription.objects.get(user=user)
            # Update existing subscription
            user_subscription.plan = plan
            user_subscription.frequency = frequency
            user_subscription.start_date = start_date # New start date for this payment
            user_subscription.end_date = end_date
            user_subscription.active = True
            user_subscription.stripe_payment_intent_id = pid # Link to the new payment intent
            user_subscription.save()
            message_content = f'SUCCESS: Existing user subscription updated for PI: {pid}.'
            print(f"Webhook Success: User {user.username}'s existing subscription updated for PI: {pid}.")
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
                    stripe_payment_intent_id=pid, # Link to the payment intent
                )
                message_content = f'SUCCESS: New user subscription created for PI: {pid}.'
                print(f"Webhook Success: New user subscription created for {user.username} for PI: {pid}.")
            except Exception as e:
                print(f"Webhook Error: Failed to create new subscription for user {user.username} for PI {pid}: {e}")
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR creating new subscription: {e}. PI: {pid}',
                    status=500 # Return 500 to tell Stripe to retry
                )

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | {message_content}',
            status=200, # Important: Always return 200 OK for Stripe webhooks if processed
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

        # Optional: Deactivate the user's subscription if a renewal payment fails
        if username and username != 'AnonymousUser':
            try:
                user = User.objects.get(username=username)
                # Find the subscription linked to this user (assuming one-to-one)
                user_subscription = UserSubscription.objects.get(user=user)
                user_subscription.active = False  # Mark subscription as inactive
                user_subscription.save()
                print(f"User {username}'s subscription marked inactive due to failed payment for PI: {pid}.")
            except User.DoesNotExist:
                print(f"Webhook Info: User {username} not found for failed payment webhook for PI: {pid}.")
            except UserSubscription.DoesNotExist:
                print(f"Webhook Info: No subscription found for user {username} to deactivate for PI: {pid}.")
            except Exception as e:
                print(f"Webhook Error: Error attempting to deactivate subscription for user {username} for PI {pid}: {e}")

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | Payment failed for PaymentIntent {pid}.',
            status=200 # Always return 200 OK for Stripe webhooks, even on failure
        )

