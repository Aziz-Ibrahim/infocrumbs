from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from preferences.models import UserPreference, Topic
from subscriptions.models import UserSubscription
from feedback.forms import CommentForm
from feedback.models import Comment, SavedCrumb
from .models import Crumb


def crumb_list(request):
    """
    View to list crumbs for authenticated and subscribed users.
    Filters crumbs by user preferences and subscription plan,
    with optional topic filtering via GET parameter.
    """
    user = request.user
    selected_topic = request.GET.get('topic')
    crumbs = Crumb.objects.none()
    saved_crumbs = []
    topics = Topic.objects.all()

    # Enforce login
    if not user.is_authenticated:
        return redirect('account_login')

    # Enforce active subscription
    subscription = UserSubscription.objects.filter(
        user=user, active=True
    ).first()
    if not subscription:
        return redirect('choose_plan')

    # Get user preferences
    pref_obj = UserPreference.objects.filter(user=user).first()
    preferred_topics = pref_obj.topics.values_list(
        'id', flat=True
    ) if pref_obj else []

    # Limit topics for basic plan
    if subscription.plan and subscription.plan.name.lower() == "basic":
        preferred_topics = list(preferred_topics)[:2]

    # Get saved crumbs
    saved_ids = []
    if request.user.is_authenticated:
        saved_ids = SavedCrumb.objects.filter(
            user=request.user
            ).values_list(
                'crumb_id', flat=True
                )

    # Filter crumbs by preferred topics
    crumbs = Crumb.objects.filter(topic__in=preferred_topics)

    # Filter by selected topic if provided
    if selected_topic:
        crumbs = crumbs.filter(topic_id=selected_topic)

    # Paginate results
    paginator = Paginator(crumbs.order_by('-published_at'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'crumbs/crumbs_list.html', {
        'page_obj': page_obj,
        'saved_ids': saved_ids,
        'topics': topics,
        'selected_topic': int(selected_topic) if selected_topic else None,
    })


def crumb_detail(request, pk):
    """
    View to display the details of a specific crumb.
    If the user is authenticated, check if the crumb is saved by the user.
    """

    crumb = get_object_or_404(Crumb, pk=pk)
    comment_form = CommentForm()
    comments = crumb.comments.select_related('user').order_by('-created_at')
    is_saved = False

    if request.user.is_authenticated:
        is_saved = SavedCrumb.objects.filter(user=request.user, crumb=crumb).exists()

    context = {
        "crumb": crumb,
        "comment_form": comment_form,
        "comments": comments,
        'is_saved': is_saved,
    }
    return render(request, "crumbs/crumb_detail.html", context)
