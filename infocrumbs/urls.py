from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # allauth
    path('accounts/', include('allauth.urls')),
    # Home page
    path('', include('core.urls')),
    # crumbs
    path('crumbs/', include('crumbs.urls')),
    path('api/crumbs/', include('crumbs.api_urls')),
    # feedback
    path('feedback/', include('feedback.urls')),
    path('api/feedback/', include('feedback.api_urls')),
    # preferences
    path('preferences/', include('preferences.urls')),
    path('api/preferences/', include('preferences.api_urls')),
    # subscriptions
    path('subscriptions/', include('subscriptions.urls')),
    path('api/subscriptions/', include('subscriptions.api_urls')),

]

