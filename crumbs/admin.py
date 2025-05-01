from django.contrib import admin
from .models import Crumb

@admin.register(Crumb)
class CrumbAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'user')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
