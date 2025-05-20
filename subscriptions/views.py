from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta

from .models import SubscriptionPlan, UserSubscription



@login_required
def choose_plan(request):
    plans = SubscriptionPlan.objects.all()
    return render(request, 'subscriptions/choose_plan.html', {'plans': plans})


@login_required
def subscribe(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    # Dummy duration logic for now
    if plan.duration == 'weekly':
        duration = timedelta(weeks=1)
    elif plan.duration == 'monthly':
        duration = timedelta(days=30)
    elif plan.duration == 'annually':
        duration = timedelta(days=365)
    else:
        duration = timedelta(days=7)

    subscription, created = UserSubscription.objects.update_or_create(
        user=request.user,
        defaults={
            'plan': plan,
            'frequency': plan.duration,
            'valid_until': now() + duration
        }
    )
    return redirect('subscription_status')


@login_required
def subscription_status(request):
    try:
        subscription = request.user.usersubscription
    except UserSubscription.DoesNotExist:
        subscription = None
    return render(request, 'subscriptions/subscription_status.html', {
        'subscription': subscription
    })
