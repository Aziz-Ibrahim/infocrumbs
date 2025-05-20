import json

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
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


@csrf_exempt
@login_required
def add_comment_api(request, crumb_id):
    if request.method == 'POST':
        crumb = get_object_or_404(Crumb, id=crumb_id)
        try:
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            if not content:
                return JsonResponse({'error': 'Empty content'}, status=400)
            comment = Comment.objects.create(
                user=request.user,
                crumb=crumb,
                content=content
            )
            return JsonResponse({
                'user': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
            })
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)