from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from datetime import timedelta
from django.shortcuts import get_object_or_404

from .models import SubscriptionPlan, UserSubscription



@require_GET
@login_required
def api_plans(request):
    plans = SubscriptionPlan.objects.all().values(
        'id', 'name', 'duration', 'price')
    return JsonResponse({'plans': list(plans)})


@require_POST
@login_required
def api_subscribe(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

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

    return JsonResponse({
        'status': 'success',
        'plan': plan.name,
        'duration': plan.duration,
        'valid_until': subscription.valid_until
    })


@require_GET
@login_required
def api_subscription_status(request):
    try:
        sub = request.user.usersubscription
        data = {
            'plan': sub.plan.name,
            'duration': sub.plan.duration,
            'valid_until': sub.valid_until
        }
    except UserSubscription.DoesNotExist:
        data = {'plan': None}

    return JsonResponse({'subscription': data})
