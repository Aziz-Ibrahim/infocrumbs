from django.urls import path
from . import api_views

urlpatterns = [
    path('plans/', api_views.api_plans, name='api_plans'),
    path('subscribe/<int:plan_id>/', api_views.api_subscribe, name='api_subscribe'),
    path('status/', api_views.api_subscription_status, name='api_subscription_status'),
]
