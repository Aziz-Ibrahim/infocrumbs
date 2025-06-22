from datetime import datetime
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required

from accounts.forms import UserUpdateForm
from preferences.models import UserPreference
from feedback.models import SavedCrumb, Comment
from subscriptions.models import UserSubscription


@login_required
def profile_view(request):
    """
    Displays the user's profile with subscription details.
    """
    user = request.user
    subscription = UserSubscription.objects.filter(
        user=user,
        active=True
        ).first()
    context = {
        'user_subscription': subscription,
    }
    return render(request, 'account/profile.html', context)


@login_required
def load_account_details(request):
    """
    Loads the user's account details for AJAX requests.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required.'}, status=401)

    # Instantiate the form with the current user's data for initial display
    form = UserUpdateForm(instance=request.user)

    html_content = render_to_string(
        "account/includes/partial_account_details.html",
        {"form": form},
        request=request
    )
    return JsonResponse({"html": html_content})


@login_required
def account_update(request):
    """
    Handles the update of user account details using a ModelForm.
    """
    user = request.user

    if request.method == "POST":
        # Instantiate the form with POST data AND the current user instance
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            # If the form is valid, save the changes to the user instance
            form.save()
            messages.success(request, "Account details updated successfully.")
            return redirect("account_profile")  # Redirect to the profile page
        else:
            # If the form is NOT valid, show error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(
                        request, f"{field.replace('_', ' ').title()}: {error}"
                        )
            return redirect("account_profile")

    return redirect("account_profile")


@login_required
def load_saved_crumbs_partial(request):
    """
    Loads the user's saved crumbs for AJAX requests.
    """
    saved_crumbs = SavedCrumb.objects.filter(
        user=request.user
        ).select_related('crumb')
    html = render_to_string(
        "account/includes/partial_saved_crumbs.html",
        {"saved_crumbs": saved_crumbs},
        request=request
    )
    return JsonResponse({"html": html})


@login_required
def load_comments_partial(request):
    """
    Loads the user's comment history for AJAX requests.
    """
    comments = Comment.objects.filter(user=request.user).select_related('crumb')
    html = render_to_string(
        "account/includes/partial_comments.html",
        {"comments": comments},
        request=request
    )
    return JsonResponse({"html": html})




@login_required
def load_preferences_partial(request):
    """
    Loads the user's topic preferences for AJAX requests.
    """
    try:
        user_preferences = UserPreference.objects.get(user=request.user)
        topics = user_preferences.topics.all()
    except UserPreference.DoesNotExist:
        topics = []

    user_subscription = UserSubscription.objects.filter(
        user=request.user,
        active=True,
        end_date__gte=now()
    )


    html = render_to_string(
        "account/includes/partial_preferences.html",
        {
            "topics": topics,
            "user_subscription": user_subscription,
        },
        request=request
    )
    return JsonResponse({"html": html})


@login_required
def load_subscription_partial(request):
    """
    Loads the user's subscription details for AJAX requests.
    """
    user_subscription = (
        UserSubscription.objects
        .filter(user=request.user)
        .select_related('plan', 'frequency')
        .first()
    )

    html = render_to_string(
        'account/includes/partial_subscription.html',
        {'user_subscription': user_subscription},
        request=request
    )

    return JsonResponse({'html': html})
