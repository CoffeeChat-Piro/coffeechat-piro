from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

def validate_img_size(image):
    if image.size > 20 * 1024* 1024:
        raise ValidationError("이미지의 최대 크기는 20MB입니다.")

class User(AbstractUser):
    username = models.CharField(max_length=30, unique=True)
    nickname = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)
    cohort = models.IntegerField(null=True, blank=True)
    email = models.EmailField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username



class Memo(models.Model):
    # user = models.ForeignKey('accounts.User', related_name='coffeechat_reviews', on_delete=models.CASCADE)
    coffeeChatRequest = models.OneToOneField('coffeechat.CoffeeChat', related_name='memo', on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)  # memo 최후 편집 시간
    content = models.CharField(max_length=5000, blank=True)     #memo 내용