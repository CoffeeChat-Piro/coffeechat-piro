from django.db import models
from django.conf import settings
# from apps.review.models import Review, Comment as ReviewComment
# from apps.trend.models import Trend, Comment as TrendComment

# class UserProfile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     profile = models.TextField(blank=True, null=True)
#     profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
#
#     def __str__(self):
#         return self.user.username