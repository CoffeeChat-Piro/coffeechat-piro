from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    FACE_TO_FACE = 'F2F'
    ONLINE = 'ONLINE'
    OFF = 'OFF'

    PROFILE_STATUS_CHOICES = [
        (FACE_TO_FACE, '대면'),
        (ONLINE, '비대면'),
        (OFF, '오프'),
    ]
    
    user = models.OneToOneField(User, related_name='received_coffeechats', on_delete=models.CASCADE)  # SET_NULL 대신 CASCADE
    job = models.CharField(max_length=10, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, related_name='coffeechats')
    content = models.TextField(null=True, blank=True)
    count = models.IntegerField(default=0)
    bookmarks = models.ManyToManyField(User, related_name='coffeechat_bookmarks', blank=True)
    profile_status = models.CharField(
        max_length=10,
        choices=PROFILE_STATUS_CHOICES,
        default=FACE_TO_FACE
    )
    is_public = models.BooleanField(default=True)

    def total_likes(self):
        return self.count

    def total_bookmark(self):
        return self.bookmarks.count()

class CoffeeChat(models.Model):
    STATUS_CHOICES = [
        ('WAITING','수락대기중'),
        ('ONGOING', '진행중'),
        ('ACCEPTED','수락'),
        ('LIMITED','최대요청횟수초과'),
        ('REJECTED', '거절'),
        ('COMPLETED', '완료')
    ]
    
    profile = models.ForeignKey(Profile, related_name='requests', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='WAITING')
    created_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True)
    letterToSenior = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Request by {self.user.username} for chat {self.profile.id}'

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=['WAITING', 'ONGOING', 'ACCEPTED', 'LIMITED', 'REJECTED', 'COMPLETED']),
                name='valid_status'
            )
        ]

class Review(models.Model):
    coffeechat_request = models.OneToOneField(CoffeeChat, related_name='review', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='coffeechat_reviews', on_delete=models.CASCADE)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.username} for request {self.coffeechat_request.id}'

class informationAgree(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    coffeechat_request = models.OneToOneField(CoffeeChat, related_name='infoAgree', on_delete=models.CASCADE)
    is_agree = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Information Agreement'
        verbose_name_plural = 'Information Agreements'

class Scrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scraps')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='scraps')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'profile']