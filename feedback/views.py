from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Comment
from .forms import CommentForm
from crumbs.models import Crumb


@login_required
def add_comment(request, crumb_id):
    if request.method == 'POST':
        crumb = get_object_or_404(Crumb, id=crumb_id)
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.crumb = crumb
            comment.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'user': comment.user.username,
                    'content': comment.content,
                    'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
                })
            return redirect('crumb_detail', pk=crumb_id)
    return JsonResponse({'error': 'Invalid request'}, status=400)
