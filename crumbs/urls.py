from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.news_view, name='news'),
    path('music/', views.music_view, name='music'),
    path('finance/', views.finance_view, name='finance'),
    path('quotes/', views.quotes_view, name='quotes'),
    path('sports/', views.sports_view, name='sports'),
    path('gardening/', views.gardening_view, name='gardening'),
]