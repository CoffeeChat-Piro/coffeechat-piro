from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)
    cohort = models.IntegerField(null=True, blank=True, help_text='몇기인지 입력하세요.')
    intro = models.TextField(null=True, blank=True, verbose_name='소개')
    phone_number = models.CharField(max_length=15, verbose_name='전화번호', help_text='전화번호를 입력하세요.')

    def __str__(self):
        return self.username