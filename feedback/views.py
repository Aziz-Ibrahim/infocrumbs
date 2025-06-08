from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Comment
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

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.crumb = crumb
            comment.save()

            html = render(
                request, "feedback/includes/comment.html", {"comment": comment}
            )
            return JsonResponse(
                {"success": True, "html": html.content.decode("utf-8")}
            )

    return JsonResponse({"success": False})


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
            html = render(
                request, "feedback/includes/comment.html", {"comment": comment}
            )
            return JsonResponse(
                {"success": True, "html": html.content.decode("utf-8")}
            )

    return JsonResponse({"success": False})


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

    if request.method == "POST":
        comment.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False})
