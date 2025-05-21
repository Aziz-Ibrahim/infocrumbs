from django.urls import path
from . import views

urlpatterns = [
    path('choose/', views.choose_plan, name='choose_plan'),
    path('subscribe/<int:plan_id>/', views.subscribe, name='subscribe'),
    path('status/', views.subscription_status, name='subscription_status'),
]
