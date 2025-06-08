from django.contrib import admin
from .models import Crumb

@admin.register(Crumb)
class CrumbAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'topic',
        'source',
        'published_at',
        'added_on'
        )
    search_fields = ('title', 'summary', 'source', "tags__name")
    list_filter = ('topic', 'source', 'published_at')
