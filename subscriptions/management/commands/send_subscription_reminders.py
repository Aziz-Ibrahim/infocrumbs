from django.core.management.base import BaseCommand
from subscriptions.email import send_subscription_expiry_reminders


class Command(BaseCommand):
    help = "Sends subscription expiry reminders"

    def handle(self, *args, **options):
        send_subscription_expiry_reminders()
