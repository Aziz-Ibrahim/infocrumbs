from django.urls import path
from . import views

urlpatterns = [
    path('set/', views.set_preferences, name='set_preferences'),
]
