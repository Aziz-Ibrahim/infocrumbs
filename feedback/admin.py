from django.contrib import admin
from .models import SavedCrumb, LikedCrumb, Comment

@admin.register(SavedCrumb)
class SavedCrumbAdmin(admin.ModelAdmin):
    list_display = ('user', 'crumb', 'saved_at')
    search_fields = ('user__username', 'crumb__title')
    list_filter = ('saved_at',)

@admin.register(LikedCrumb)
class LikedCrumbAdmin(admin.ModelAdmin):
    list_display = ('user', 'crumb', 'liked_at')
    search_fields = ('user__username', 'crumb__title')
    list_filter = ('liked_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'crumb', 'created_at')
    search_fields = ('user__username', 'crumb__title', 'content')
    list_filter = ('created_at',)