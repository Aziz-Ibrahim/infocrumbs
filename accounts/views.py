from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from preferences.models import Topic
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
    if request.method == 'POST':
        user = request.user  # This is your CustomUser instance

        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()

        # might want to validate that the new email isn't already taken
        user.save()
        messages.success(request, "Account details updated successfully.")

    return render('account/includes/partial_account_details.html', {
        'user': request.user
    })


@login_required
def load_saved_crumbs_partial(request):
    saved_crumbs = SavedCrumb.objects.filter(user=request.user).select_related('crumb')
    return render(request, "account/includes/partial_saved_crumbs.html", {
        "saved_crumbs": saved_crumbs
    })


@login_required
def load_comments_partial(request):
    comments = Comment.objects.filter(user=request.user).select_related('crumb')
    return render(request, "accounts/includes/partial_comments.html", {
        "comments": comments
    })


@login_required
def load_preferences_partial(request):
    user_topics = request.user.profile.topics.all()
    return render(request, "account/includes/partial_preferences.html", {
        "topics": user_topics
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

