from django.urls import path
from . import views, api_views

urlpatterns = [
    path('choose/', views.choose_plan, name='choose_plan'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('status/', views.subscription_status, name='subscription_status'),
    path('plans/', api_views.api_plans, name='api_plans'),
    path('subscribe/<int:plan_id>/', api_views.api_subscribe, name='api_subscribe'),
    path('status/', api_views.api_subscription_status, name='api_subscription_status'),
]
