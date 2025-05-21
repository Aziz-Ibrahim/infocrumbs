import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import Topic, UserPreference

@csrf_exempt
@login_required
def user_preferences_api(request):
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        selected_ids = list(preferences.topics.values_list('id', flat=True))
        all_topics = list(Topic.objects.values('id', 'name', 'description'))
        return JsonResponse({
            'selected_topic_ids': selected_ids,
            'all_topics': all_topics
        })

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            topic_ids = data.get('topics', [])
            preferences.topics.set(topic_ids)
            return JsonResponse({'status': 'updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)