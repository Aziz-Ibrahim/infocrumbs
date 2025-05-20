from django.urls import path
from . import views

urlpatterns = [
    path('', views.crumb_list, name='crumb_list'),
    path('<int:pk>/', views.crumb_detail, name='crumb_detail'),
    path('api/crumbs/', views.infinite_crumbs, name='infinite_crumbs_api'),
]