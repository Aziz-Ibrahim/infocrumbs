from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from preferences.models import UserPreference
from feedback.models import SavedCrumb, Comment
from subscriptions.models import UserSubscription
from subscriptions.views import choose_plan 


@login_required
def profile_view(request):
    return render(request, 'account/profile.html')


@login_required
def load_account_details(request):
    return render(request, 'account/includes/partial_account_details.html',{
        'user': request.user
    })



@login_required
def account_update(request):
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name = request.POST.get("last_name", user.last_name)
        user.email = request.POST.get("email", user.email)

        user.save()
        messages.success(request, "Account details updated successfully.")

    return redirect("profile")


@login_required
def load_saved_crumbs_partial(request):
    saved_crumbs = SavedCrumb.objects.filter(user=request.user).select_related('crumb')
    return render(request, "account/includes/partial_saved_crumbs.html", {
        "saved_crumbs": saved_crumbs
    })


@login_required
def load_comments_partial(request):
    comments = Comment.objects.filter(user=request.user).select_related('crumb')
    return render(request, "account/includes/partial_comments.html", {
        "comments": comments
    })



@login_required
def load_preferences_partial(request):
    try:
        user_preferences = UserPreference.objects.get(user=request.user)
        topics = user_preferences.topics.all()
    except UserPreference.DoesNotExist:
        topics = []

    return render(request, "account/includes/partial_preferences.html", {
        "topics": topics
    })


@login_required
def load_subscription_partial(request):
    try:
        subscription = request.user.usersubscription
    except UserSubscription.DoesNotExist:
        subscription = None
    return render(request, 'account/includes/partial_subscription.html', {
        'subscription': subscription
    })

