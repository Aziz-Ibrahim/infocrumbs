from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')),
    path('crumbs/', include('crumbs.urls')),
    path('payments/', include('payments.urls')),
]
