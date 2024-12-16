from django.db import models

from apps import coffeechat
from apps.accounts.models import CustomUser
from django.utils import timezone

class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name  # 해시태그의 이름을 반환

class CoffeeChat(models.Model):
    sender = models.ForeignKey(CustomUser, related_name='sent_coffeechats', on_delete=models.SET_NULL, null=True, blank=True)  # 커피챗 요청을 보낸 사람
    receiver = models.ForeignKey(CustomUser, related_name='received_coffeechats', on_delete=models.SET_NULL, null=True, blank=True) # 커피챗 요청을 받은 사람
    job = models.CharField(max_length=10, null=False) #직업
    created_at = models.DateTimeField(auto_now_add=True) #요청시간
    hashtags = models.ManyToManyField(Hashtag, related_name='coffeechats') #해시태그
    content = models.TextField(null=True, blank=True) #자기소개
    count = models.IntegerField(default=0) #요청 수
    bookmarks = models.ManyToManyField(CustomUser, related_name='coffeechat_bookmarks', blank=True) #북마크
    is_public = models.BooleanField(default=True)  # 기본적으로 공개

    # def date(self):
    #     return self.created_at
    def total_likes(self):
        return self.count
    def total_bookmark(self):
        return self.bookmarks.count()

class CoffeeChatRequest(models.Model):
    STATUS_CHOICES = [
        ('WAITING','수락대기중'),
        ('ACCEPTED','수락'),
        ('LIMITED','최대요청횟수초과'),
        ('PRIVATE','비공개'),
        ('REJECTED', '거절'),
    ]
    
    coffeechat = models.ForeignKey(CoffeeChat, related_name='requests', on_delete=models.CASCADE) # 커피챗 프로필 정보
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) # 요청한 사용자
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='WAITING') #요청한 사용자에 따른 현재 상태
    created_at = models.DateTimeField(default=timezone.now) # 요청 생성 시간
    letterToSenior = models.TextField(null=True, blank=True) #선배에게 보내는 편지

    def __str__(self):
        return f'Request by {self.user.username} for chat {self.coffeechat.id}'

class Review(models.Model):
    coffeechat_request = models.OneToOneField(CoffeeChatRequest, related_name='review', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(CustomUser, related_name='coffeechat_reviews', on_delete=models.CASCADE)  # 리뷰를 작성한 사용자
    rating = models.IntegerField(default=0)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 리뷰 작성 시간

    def __str__(self):
        return f'Review by {self.reviewer.username} for request {self.coffeechat_request.id}'


class informationAgree(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) # 동의한 사람
    date = models.DateTimeField(default=timezone.now) #동의 시간
    coffeechat_request = models.OneToOneField(CoffeeChatRequest, related_name='infoAgree', on_delete=models.CASCADE)
    is_agree = models.BooleanField(default=False)
