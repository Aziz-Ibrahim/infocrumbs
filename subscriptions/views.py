from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta

from .models import SubscriptionPlan, UserSubscription, SubscriptionFrequency
from .utils import calculate_subscription_price

def choose_plan(request):
    plans = SubscriptionPlan.objects.all()
    frequencies = SubscriptionFrequency.objects.all()

    plan_options = []

    for plan in plans:
        frequency_options = []

        for freq in frequencies:
            price = calculate_subscription_price(plan.name, freq.duration_days)

            if price is not None:
                frequency_options.append({
                    'id': freq.id,
                    'name': freq.name,
                    'discount': freq.discount_percent,
                    'price': price,
                })
            else:
                print(f"Warning: Could not calculate price for plan '{plan.name}' and duration '{freq.duration_days}'")


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

    final_price = calculate_subscription_price(plan.name, frequency.duration_days)

    if final_price is None:
        return redirect('choose_plan')


    context = {
        'plan': plan,
        'frequency': frequency,
        'plan_id': plan.id,
        'frequency_id': frequency.id,
        'price': final_price,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    }

    return render(request, 'checkout/checkout.html', context)


@login_required
def subscription_status(request):
    try:
        subscription = request.user.usersubscription
    except UserSubscription.DoesNotExist:
        subscription = None
    return render(request, 'subscriptions/subscription_status.html', {
        'subscription': subscription
    })
