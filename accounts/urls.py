from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.profile_view, name="account_profile"),
    path('profile/account-details/', views.load_account_details, name='load_account_details_partial'),
    path('profile/saved-crumbs/', views.load_saved_crumbs_partial, name='load_saved_crumbs_partial'),
    path('profile/comments/', views.load_comments_partial, name='load_comments_partial'),
    path('profile/preferences/', views.load_preferences_partial, name='load_preferences_partial'),
    path('profile/subscription/', views.load_subscription_partial, name='load_subscription_partial'),
]
