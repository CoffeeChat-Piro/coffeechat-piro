# 표준 라이브러리
from datetime import timedelta
from django.contrib.auth.decorators import login_required
# Django 모듈
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone

# 프로젝트 내 모듈
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from ..coffeechat.models import Profile
# from ..corboard.models import Corboard
# from ..review.models import Review
# from ..trend.models import Trend


def index(request):
    return render(request, 'accounts/login.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('accounts:onboarding')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('coffeechat:main')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def onboarding(request):
    if request.method == 'POST':
        if 'mentor' in request.POST:
            # 멘토로 참여하기 선택 시
            return redirect('coffeechat:coffeechat_create')
        elif 'mentee' in request.POST:
            # 멘티로 참여하기 선택 시
            return redirect('coffeechat:main')
    return render(request, 'accounts/onboarding.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:login')

def find_most_popular(items):
    now = timezone.now()
    most_popular_item = None
    highest_score = 0
    G = 1.8  # 시간 가중치

    # 각 항목에 대해 인기 점수 계산
    for item in items:
        time_diff_hours = (now - item.date).total_seconds() / 3600
        score = (item.total_likes() + item.total_bookmark()) / (time_diff_hours + 2) ** G
        print("reviews score:", score)


    # 현재 항목의 점수가 최고 점수보다 높으면 업데이트
        if score > highest_score:
            highest_score = score
            most_popular_item = item
        print(item.title, score)
    return most_popular_item

def find_most_popular_coffeeChat(items):
    now = timezone.now()
    most_popular_item = None
    highest_score = 0
    G = 1.8  # 시간 가중치
    print("Items",items)
    # 각 항목에 대해 인기 점수 계산
    for item in items:
        print(item.content)
        time_diff_hours = (now - item.created_at).total_seconds() / 3600
        score = (item.total_likes() + item.total_bookmark()) / (time_diff_hours + 2) ** G
        print("coffeechat:", score)

        # 현재 항목의 점수가 최고 점수보다 높으면 업데이트
        if score > highest_score:
            highest_score = score
            most_popular_item = item

    return most_popular_item