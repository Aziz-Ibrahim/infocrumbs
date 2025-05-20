from django.urls import path
from . import views

urlpatterns = [
    path('comment/<int:crumb_id>/', views.add_comment, name='add_comment'),
    path('api/comment/<int:crumb_id>/', views.add_comment,
         name='add_comment_api'),
]
