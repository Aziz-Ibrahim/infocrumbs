from django.contrib import admin
from .models import Topic, UserPreference


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user',)
    filter_horizontal = ('topics',)  # Enables multi-select interface
