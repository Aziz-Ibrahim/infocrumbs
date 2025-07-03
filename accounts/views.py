from datetime import datetime
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import CustomUser
from .forms import UserUpdateForm
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
    Handles the update of user account details using a ModelForm via AJAX POST.
    Returns JSON with rendered HTML containing the form 
    (with errors or updated data).
    """
    user = request.user

    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Account details updated successfully.")
            # Re-instantiate the form with the updated user data
            # so the rendered HTML shows the new values
            form = UserUpdateForm(instance=user)
        else:
            # If the form is NOT valid, add a general error message.
            # Field-specific errors will be displayed by the template.
            messages.error(request, "Please correct the errors below.")
        
        # Render the partial HTML template with the form 
        # (either valid or invalid)
        html_content = render_to_string(
            "account/includes/partial_account_details.html",
            {
                'form': form,
                'user': user, # Pass user if needed in partial template
            },
            request=request
        )
        return JsonResponse({"html": html_content})
    else:
        # If a GET request somehow hits this endpoint directly,
        # redirect to the main profile page.
        return redirect("account_profile")


@login_required
def load_saved_crumbs_partial(request):
    """
    Loads the user's saved crumbs with pagination for AJAX requests.
    Shows 5 items per page.
    """
    saved_crumbs_list = SavedCrumb.objects.filter(
        user=request.user
    ).select_related('crumb').order_by('-saved_at')

    paginator = Paginator(saved_crumbs_list, 3)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    html_content = render_to_string(
        "account/includes/partial_saved_crumbs.html",
        {
            "page_obj": page_obj,
            "saved_crumbs": page_obj.object_list,
        },
        request=request
    )

    return JsonResponse({
        "html": html_content,
        "has_next_page": page_obj.has_next(),
        # Call next_page_number() as a method
        "next_page_number": (
            page_obj.next_page_number() if page_obj.has_next() else None
        ),
    })


@login_required
def load_comments_partial(request):
    """
    Loads the user's comment history with pagination for AJAX requests.
    Shows 5 items per page.
    """
    comments_list = Comment.objects.filter(
        user=request.user
    ).select_related('crumb').order_by('-created_at')

    paginator = Paginator(comments_list, 2)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    html_content = render_to_string(
        "account/includes/partial_comments.html",
        {
            "page_obj": page_obj,
            "comments": page_obj.object_list,
        },
        request=request
    )

    return JsonResponse({
        "html": html_content,
        "has_next_page": page_obj.has_next(),
        # Call next_page_number() as a method
        "next_page_number": (
            page_obj.next_page_number() if page_obj.has_next() else None
        ),
    })


def load_preferences_partial(request):
    # Ensure user is authenticated for this AJAX request
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'Authentication required. Please log in.'},
            status=401
        )

    topics_list = []
    user_subscription = None

    try:
        user_preferences = UserPreference.objects.get(user=request.user)
        topics_list = user_preferences.topics.all().order_by('name')
    except UserPreference.DoesNotExist:
        topics_list = []
    except Exception as e:
        print(f"Error fetching user preferences or topics: {e}")
        return JsonResponse(
            {'error': 'An internal error occurred while retrieving preferences.'},
            status=500)

    try:
        user_subscription = request.user.subscriptions.filter(
            active=True,
            end_date__gte=timezone.now()
        ).first()
    except Exception as e:
        print(f"Error fetching user subscription: {e}")
        pass

    # Pagination for topics
    paginator = Paginator(topics_list, 2)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    html_content = render_to_string(
        "account/includes/partial_preferences.html",
        {
            "page_obj": page_obj,
            "topics": page_obj.object_list,
            "user_subscription": user_subscription,
        },
        request=request
    )
    
    return JsonResponse({
        "html": html_content,
        "has_next_page": page_obj.has_next(),
        # Call next_page_number() as a method
        "next_page_number": (
            page_obj.next_page_number() if page_obj.has_next() else None
        ),
    })


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
