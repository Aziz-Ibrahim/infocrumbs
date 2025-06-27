from django.urls import path
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('faq/', views.faq_view, name='faq'),
    path('contact/', views.contact_view, name='contact'),
    # Authentication URLs
    path('signup/', lambda request: redirect('account_signup'), name='signup'),
    path('login/', lambda request: redirect('account_login'), name='login'),
    path('logout/', lambda request: redirect('account_logout'), name='logout'),
]