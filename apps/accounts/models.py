from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.coffeechat.models import CoffeeChatRequest


class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)
    cohort = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.username


class Memo(models.Model):
    user = models.ForeignKey(CustomUser, related_name='coffeechat_reviews', on_delete=models.CASCADE)  # memo를 작성한 사용자
    coffeeChatRequest = models.OneToOneField(CoffeeChatRequest, related_name='review', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)  # memo 최후 편집 시간
    content = models.CharField(max_length=5000, blank=True)     #memo 내용

