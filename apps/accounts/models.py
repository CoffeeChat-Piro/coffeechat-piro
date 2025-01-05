# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.coffeechat.models import CoffeeChat


def validate_img_size(image):
    if image.size > 20 * 1024 * 1024:  # 20MB
        raise ValidationError("이미지의 최대 크기는 20MB입니다.")

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    nickname = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True,
        validators=[validate_img_size]
    )
    cohort = models.IntegerField(null=True, blank=True)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # auto_now_add를 auto_now로 수정

    def __str__(self):
        return self.username

class Memo(models.Model):
    user = models.ForeignKey(User, related_name='memos', on_delete=models.CASCADE)
    coffeeChatRequest = models.OneToOneField(CoffeeChat, related_name='memo', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.CharField(max_length=5000, blank=True)

    def __str__(self):
        return f'Memo by {self.user.username} for coffee chat request {self.coffeeChatRequest.id}'