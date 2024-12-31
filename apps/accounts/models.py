from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True)
    cohort = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.username