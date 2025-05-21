from django.urls import path
from . import api_views

urlpatterns = [
     path('api/comment/<int:crumb_id>/', api_views.add_comment_api,
         name='add_comment_api'),
]
