from django.db import models
from django.conf import settings

from crumbs.models import Crumb


class SavedCrumb(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    crumb = models.ForeignKey(Crumb, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'crumb']

    def __str__(self):
        return f"{self.user.username} saved {self.crumb.title}"


class LikedCrumb(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    crumb = models.ForeignKey(Crumb, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'crumb']

    def __str__(self):
        return f"{self.user.username} liked {self.crumb.title}"
