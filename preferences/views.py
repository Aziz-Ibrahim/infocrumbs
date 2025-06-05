import datetime

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

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
    try:
        user_subscription = request.user.usersubscription
        if not user_subscription.active or \
            user_subscription.end_date < timezone.now():
                return redirect('choose_plan')
    except UserSubscription.DoesNotExist:
        return redirect('choose_plan')


    user_preference_obj, created = \
        UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserPreferenceForm(
            request.POST,
            instance=user_preference_obj,
            user=request.user
            )
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserPreferenceForm(
            instance=user_preference_obj,
            user=request.user
            )

    return render(request, 'preferences/set_preferences.html', {'form': form})