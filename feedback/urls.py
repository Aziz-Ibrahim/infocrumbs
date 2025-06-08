from django.urls import path
from . import views

urlpatterns = [
    path(
        'comment/add/<int:crumb_id>/', views.add_comment, name='add_comment'
    ),
    path(
        'comment/edit/<int:comment_id>/',
        views.edit_comment, name='edit_comment'
    ),
    path(
        'comment/delete/<int:comment_id>/',
        views.delete_comment, name='delete_comment'
    ),
]
