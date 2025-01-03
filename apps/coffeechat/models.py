from django.db import models

from apps import coffeechat
from apps.accounts.models import User
from django.utils import timezone

class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name  # 해시태그의 이름을 반환

class Profile(models.Model):
    FACE_TO_FACE = 'F2F'
    ONLINE = 'ONLINE'
    OFF = 'OFF'

    PROFILE_STATUS_CHOICES = [
        (FACE_TO_FACE, '대면'),
        (ONLINE, '비대면'),
        (OFF, '오프'),
    ]
    
    sender = models.ForeignKey(User, related_name='sent_coffeechats', on_delete=models.SET_NULL, null=True, blank=True)  # 커피챗 요청을 보낸 사람
    receiver = models.ForeignKey(User, related_name='received_coffeechats', on_delete=models.SET_NULL, null=True, blank=True) # 커피챗 요청을 받은 사람
    job = models.CharField(max_length=10, null=False) #직업
    created_at = models.DateTimeField(auto_now_add=True) #요청시간
    hashtags = models.ManyToManyField(Hashtag, related_name='coffeechats') #해시태그
    content = models.TextField(null=True, blank=True) #자기소개
    count = models.IntegerField(default=0) #요청 수
    bookmarks = models.ManyToManyField(User, related_name='coffeechat_bookmarks', blank=True) #북마크
    profile_status = models.CharField(
        max_length=10,
        choices=PROFILE_STATUS_CHOICES,
        default=FACE_TO_FACE  # 기본값 설정
    )

    # def date(self):
    #     return self.created_at
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
        ('PRIVATE','비공개'),
        ('REJECTED', '거절'),
        ('COMPLETED', '완료')
    ]
    
    coffeechat = models.ForeignKey(Profile, related_name='requests', on_delete=models.CASCADE) # 커피챗 프로필 정보
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 요청한 사용자
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='WAITING') #요청한 사용자에 따른 현재 상태
    created_at = models.DateTimeField(default=timezone.now) # 요청 생성 시간
    letterToSenior = models.TextField(null=True, blank=True) #선배에게 보내는 편지

    def __str__(self):
        return f'Request by {self.user.username} for chat {self.coffeechat.id}'

class Review(models.Model):
    coffeechat_request = models.OneToOneField(CoffeeChat, related_name='review', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, related_name='coffeechat_reviews', on_delete=models.CASCADE)  # 리뷰를 작성한 사용자
    rating = models.IntegerField(default=5)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 리뷰 작성 시간

    def __str__(self):
        return f'Review by {self.reviewer.username} for request {self.coffeechat_request.id}'


#현재는 사용하지 않는 동의?
class informationAgree(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 동의한 사람
    date = models.DateTimeField(default=timezone.now) #동의 시간
    coffeechat_request = models.OneToOneField(CoffeeChat, related_name='infoAgree', on_delete=models.CASCADE)
    is_agree = models.BooleanField(default=False)
