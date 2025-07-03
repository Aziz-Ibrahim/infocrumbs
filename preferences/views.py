from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from subscriptions.models import UserSubscription
from .forms import UserPreferenceForm
from .models import UserPreference


@login_required
def set_preferences(request):
    """
    Allows a logged-in user to set their preferences.

    Requires an active subscription; redirects to 'choose_plan' if not.
    Handles both GET (display form) and POST (process form) requests.
    """
    # Get the latest valid subscription
    user_subscription = UserSubscription.objects.filter(
        user=request.user,
        active=True,
        end_date__gte=now()
    ).order_by('-end_date').first()

    if not user_subscription:
        return redirect('choose_plan')

    # Get or create preferences object
    user_preference_obj, _ = UserPreference.objects.get_or_create(
        user=request.user
    )

    # Handle form
    if request.method == 'POST':
        form = UserPreferenceForm(
            request.POST,
            instance=user_preference_obj,
            user=request.user,
        )
        if form.is_valid():
            form.save()
            return redirect('crumb_list')
    else:
        form = UserPreferenceForm(
            instance=user_preference_obj,
            user=request.user,
        )

    return render(request, 'preferences/set_preferences.html', {
        'form': form,
    })
