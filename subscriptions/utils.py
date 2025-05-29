from .models import SubscriptionPlan, SubscriptionFrequency

def calculate_subscription_price(plan_name, duration_days):
    """
    Calculates the subscription price based on plan name and duration.
    Assumes SubscriptionPlan has a 'price' field
    representing its base cost (e.g., monthly).
    """
    try:
        plan = SubscriptionPlan.objects.get(name=plan_name)
    except SubscriptionPlan.DoesNotExist:
        return None

    try:
        frequency = SubscriptionFrequency.objects.get(
            duration_days=duration_days
            )
        discount_percent = frequency.discount_percent
    except SubscriptionFrequency.DoesNotExist:
        discount_percent = 0 # No discount if frequency not found

    MONTH_DAYS = 30
    number_of_billing_units = duration_days / MONTH_DAYS

    raw_total_price = float(plan.price) * number_of_billing_units

    discount_amount = raw_total_price * (discount_percent / 100)
    final_price = raw_total_price - discount_amount

    return round(final_price, 2)