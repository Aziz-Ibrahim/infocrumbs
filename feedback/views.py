from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Comment, SavedCrumb
from .forms import CommentForm
from crumbs.models import Crumb


@login_required
def add_comment(request, crumb_id):
    """
    Add a comment to a Crumb.
    This view handles both GET and POST requests. For GET requests,
    it returns a form for adding a comment. For POST requests,
    it processes the form submission and saves the comment.
    If the request is an AJAX request, it returns a JSON response
    with the comment details. Otherwise, it redirects to the Crumb detail page.
    """
    crumb = get_object_or_404(Crumb, id=crumb_id)

    if request.method == "POST" and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.crumb = crumb
            comment.user = request.user
            comment.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                comments = crumb.comments.order_by("-created_at")
                return render(request, "feedback/includes/comment_list.html", {
                    "comments": comments,
                    "user": request.user
                })

            return redirect("crumb_detail", pk=crumb.id)

    return HttpResponseBadRequest("Invalid comment or unauthenticated.")


@login_required
def edit_comment(request, comment_id):
    """
    Edit an existing comment.
    This view allows a user to edit their own comment on a Crumb.
    It retrieves the comment by its ID and checks if it belongs to the user.
    If the request method is POST, it processes the form submission.
    If the form is valid, it saves the changes and returns a JSON response
    with the updated comment HTML. If the request is not valid, it returns
    a JSON response indicating failure.
    """
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "content": comment.content,
                })

            # fallback if not AJAX
            return redirect("crumb_detail", pk=comment.crumb.id)

        else:
            return JsonResponse(
                {"success": False, "errors": form.errors}, status=400
            )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return render(request, "feedback/includes/edit_comment_form.html", {
            "form": CommentForm(instance=comment),
            "comment": comment
        })

    return HttpResponseBadRequest("Invalid request.")


@login_required
def delete_comment(request, comment_id):
    """
    Delete a comment.
    This view allows a user to delete their own comment on a Crumb.
    It retrieves the comment by its ID and checks if it belongs to the user.
    If the request method is POST, it deletes the comment and returns a JSON
    response indicating success. If the request is not valid, it returns
    a JSON response indicating failure.
    """
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST' and \
        request.headers.get('x-requested-with') == 'XMLHttpRequest':
        comment.delete()
        return JsonResponse({'success': True})
    return HttpResponseBadRequest("Invalid request")


@login_required
def toggle_save_crumb(request, crumb_id):
    """
    Toggle saving a Crumb.
    This view allows a user to save or unsave a Crumb.
    Retrieves the Crumb by its ID and checks if the user has already saved it.
    If the Crumb is already saved, it deletes the SavedCrumb entry and returns
    a JSON response indicating that the Crumb is no longer saved.
    If the Crumb is not saved, it creates a new SavedCrumb entry and returns
    a JSON response indicating that the Crumb is now saved.
    """
    crumb = get_object_or_404(Crumb, id=crumb_id)
    saved, created = SavedCrumb.objects.get_or_create(
        user=request.user, crumb=crumb
    )

    if not created:
        saved.delete()
        return JsonResponse({"saved": False})
    return JsonResponse({"saved": True})