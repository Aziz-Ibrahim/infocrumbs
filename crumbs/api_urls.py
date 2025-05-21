from django.urls import path
from . import api_views

urlpatterns = [
    path('infinite/', api_views.infinite_crumbs, name='infinite_crumbs_api'),
    path('<int:pk>/', api_views.crumb_detail_api, name='crumb_detail_api'),
]
