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
from ..coffeechat.models import CoffeeChat
# from ..corboard.models import Corboard
# from ..review.models import Review
# from ..trend.models import Trend


def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('accounts:start')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:start')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('accounts:index')
@login_required
def start(req):
    now = timezone.now()

    three_months_ago = now - timedelta(days=90)

    #인기있는 project review
    # reviews = Review.objects.filter(date__gte=three_months_ago)
    # print("reviews count:", reviews.count())
    # review_most = find_most_popular(reviews)

    # corboards = Corboard.objects.filter(date__gte=three_months_ago)
    # coboard_most = find_most_popular(corboards)

    coffeechats = CoffeeChat.objects.filter(created_at__gte=three_months_ago)
    coffeechat_most = find_most_popular_coffeeChat(coffeechats)

    # trends = Trend.objects.filter(date__gte=three_months_ago)
    # trend_most = find_most_popular(trends)

    ctx = {
    #     'review_most': review_most,
    #     'coboard_most': coboard_most,
        'coffeechat_most': coffeechat_most,
    #     'trend_most': trend_most,
    }

    return render(req, 'accounts/start.html', ctx)

#===========================
#main page 기능 구성
#===========================

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