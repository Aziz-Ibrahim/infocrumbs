from django.contrib import admin
from .models import SubscriptionPlan, SubscriptionFrequency, UserSubscription

admin.site.register(SubscriptionPlan)
admin.site.register(SubscriptionFrequency)
admin.site.register(UserSubscription)
