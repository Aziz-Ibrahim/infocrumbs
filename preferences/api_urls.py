from django.urls import path
from . import api_views

urlpatterns = [
    path('api/user-preferences/', api_views.user_preferences_api,
         name='user_preferences_api'),
]
