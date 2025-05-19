from django.db import models
from django.conf import settings

from crumbs.models import Crumb


class SavedCrumb(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_crumbs'
    )
    crumb = models.ForeignKey(Crumb, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'crumb'],
                                    name='unique_saved_crumb')
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.crumb.title}"


class LikedCrumb(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_crumbs'
    )
    crumb = models.ForeignKey(Crumb, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'crumb'],
                                    name='unique_liked_crumb')
        ]

    def __str__(self):
        return f"{self.user.username} liked {self.crumb.title}"
    

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE)
    crumb = models.ForeignKey(Crumb, on_delete=models.CASCADE,
                            related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.crumb.title}"
