from django.urls import path
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', lambda request: redirect('account_signup')),
    path('login/', lambda request: redirect('account_login')),
    path('logout/', lambda request: redirect('account_logout')),
]