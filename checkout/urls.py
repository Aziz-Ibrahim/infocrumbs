from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path("create-payment-intent/", views.create_payment_intent, name="create_payment_intent"),
]
