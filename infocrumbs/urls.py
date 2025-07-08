from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 404
handler404 = 'core.views.custom_404_view'

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
    # feedback
    path('feedback/', include('feedback.urls')),
    # preferences
    path('preferences/', include('preferences.urls')),
    # subscriptions
    path('subscriptions/', include('subscriptions.urls')),
    # checkout
    path('checkout/', include('checkout.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

