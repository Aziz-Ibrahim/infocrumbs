from django.urls import path
from . import views
from . import webhooks


urlpatterns = [
    # Main checkout view, takes plan_id and frequency_id
    path('<int:plan_id>/<int:frequency_id>/', views.checkout_subscription, name='checkout'),
    # AJAX endpoint to cache checkout data in PaymentIntent metadata
    path('cache_checkout_data/', views.cache_checkout_data, name='cache_checkout_data'),
    # Stripe webhook endpoint
    path('wh/', webhooks.webhook, name='webhook'),
    # Success page after payment
    path('success/<str:payment_intent_id>/', views.checkout_success, name='checkout_success'),
]
