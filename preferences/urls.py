from django.urls import path
from . import views

urlpatterns = [
    path('set/', views.set_preferences, name='set_preferences'),
    path('api/user-preferences/', views.user_preferences_api,
         name='user_preferences_api'),
]
