import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

from .models import Comment
from crumbs.models import Crumb

@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
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
            }, content_type='application/json')

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400,
                                content_type='application/json')
    
    return JsonResponse({'error': 'Invalid request method'}, status=405,
                        content_type='application/json')
