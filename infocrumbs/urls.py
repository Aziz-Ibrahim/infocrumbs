from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # allauth
    path('accounts/', include('allauth.urls')),
    # accounts
    path('accounts/', include('accounts.urls')),
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
    # checkout
    path('checkout/', include('checkout.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

