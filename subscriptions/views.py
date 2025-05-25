from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta

from .models import SubscriptionPlan, UserSubscription, SubscriptionFrequency


def choose_plan(request):
    plans = SubscriptionPlan.objects.all()
    frequencies = SubscriptionFrequency.objects.all()

    # base weekly prices — could be moved into DB later
    base_prices = {
        'basic': 5,
        'premium': 10,
    }

    plan_options = []

    for plan in plans:
        base_price = base_prices.get(plan.name, 5)
        frequency_options = []

        for freq in frequencies:
            weeks = freq.duration_days / 7
            full_price = base_price * weeks
            discounted_price = full_price * (1 - (freq.discount_percent / 100))

            frequency_options.append({
                'id': freq.id,
                'name': freq.name,
                'discount': freq.discount_percent,
                'price': round(discounted_price, 2),
            })

        plan_options.append({
            'id': plan.id,
            'name': plan.get_name_display(),
            'topic_limit': plan.topic_limit,
            'frequencies': frequency_options
        })

    return render(request, 'subscriptions/choose_plan.html', {
        'plans': plan_options
    })



@login_required
def subscribe(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    frequency_id = request.GET.get('frequency')

    if not frequency_id:
        return redirect('choose_plan')

    frequency = get_object_or_404(SubscriptionFrequency, id=frequency_id)

    duration = timedelta(days=frequency.duration_days)
    expires_at = now() + duration

    subscription, created = UserSubscription.objects.update_or_create(
        user=request.user,
        defaults={
            'plan': plan,
            'frequency': frequency,
            'expires_at': expires_at
        }
    )
    return redirect('account_profile')



@login_required
def subscription_status(request):
    try:
        subscription = request.user.usersubscription
    except UserSubscription.DoesNotExist:
        subscription = None
    return render(request, 'subscriptions/subscription_status.html', {
        'subscription': subscription
    })
