# 표준 라이브러리
import json
from datetime import timedelta

# Django 모듈
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from apps.coffeechat.forms import WayToContect
from django.core.paginator import Paginator

# 프로젝트 내 모듈
from .mailing_service import send_request_mail, send_accept_mail, send_reject_mail
from .models import Profile, Hashtag, CoffeeChat, Review, User, informationAgree, Scrap
from .forms import CoffeeChatForm, ReviewForm, CoffeechatRequestForm

User = get_user_model()

@login_required
def home(request):
    query = request.GET.get('search')
    profile_status_filter = request.GET.get('status')
    page = request.GET.get('page', 1)
    
    items_per_page = 8  # 기본값 8개
    if request.GET.get('mobile') == 'true':
        items_per_page = 6

    profiles = Profile.objects.all()

    if query:
        profiles = profiles.filter(
            Q(hashtags__name__icontains=query) |
            Q(user__username__icontains=query)
        ).distinct()

    if profile_status_filter:
        profiles = profiles.filter(profile_status=profile_status_filter)
    
    # 현재 로그인한 사용자의 프로필 제외
    profiles = profiles.exclude(user=request.user)
    
    # 페이지네이션
    paginator = Paginator(profiles, items_per_page)
    page_obj = paginator.get_page(page)
    
    user_profile = Profile.objects.filter(user=request.user).first()
    
    waiting_requests = CoffeeChat.objects.filter(profile__user=request.user, status='WAITING').count()
    is_limited = waiting_requests >= 2 or (user_profile and user_profile.count >= 2)
   
    context = {
        "profiles": page_obj,
        "is_limited": is_limited,
        "user_has_profile": bool(user_profile),
        "user_profile_id": user_profile.id if user_profile else None
    }
    return render(request, 'coffeechat/main.html', context)

@login_required
def create(req):
    existing_profile = Profile.objects.filter(user=req.user).first()
    if existing_profile:
        return redirect('coffeechat:coffeechat_detail', pk=existing_profile.pk)

    if req.method == "POST":
        form = CoffeeChatForm(req.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = req.user
            profile.count = 0
            profile.content = form.cleaned_data['content']
            profile.profile_status = form.cleaned_data['profile_status']
            profile.save()
            
            hashtags = form.cleaned_data['hashtags']
            hashtag_list = json.loads(hashtags)
            hashtag_objects = []
            for tag in hashtag_list:
                hashtag, created = Hashtag.objects.get_or_create(name=tag)
                hashtag_objects.append(hashtag)
            profile.hashtags.set(hashtag_objects)
            
            return redirect('coffeechat:coffeechat_detail', pk=profile.pk)
    else:
        form = CoffeeChatForm()
    return render(req, 'coffeechat/chatcreate.html', {'form': form})

@csrf_protect
@login_required
def create_review(request, coffeechat_request_id):
    coffeechat_request = get_object_or_404(CoffeeChat, id=coffeechat_request_id)

    if request.user != coffeechat_request.user:
        return HttpResponseForbidden("리뷰 작성 권한이 없습니다.")

    if hasattr(coffeechat_request, 'review'):
        return render(request, 'coffeechat/review_form.html', {
            'error_message': '이미 이 요청에 대한 리뷰가 작성되었습니다.'
        })

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.coffeechat_request = coffeechat_request
            review.save()

            return redirect('coffeechat:coffeechat_detail', pk=coffeechat_request.profile.pk)
    else:
        form = ReviewForm()
    return render(request, 'coffeechat/review_form.html', {'form': form})

def detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    reviews = Review.objects.filter(coffeechat_request__profile=profile)

    has_pending_request = CoffeeChat.objects.filter(
        user=profile.user,
        profile__user=request.user,
        status='WAITING'
    ).exists()

    if request.method == "POST" and request.user != profile.user:
        profile_requests = CoffeeChat.objects.filter(
            profile=profile,
            status__in=['WAITING', 'ONGOING', 'ACCEPTED', 'COMPLETED']
        ).count()

        if profile_requests < 2:
            form = CoffeechatRequestForm(request.POST)
            if form.is_valid():
                #요청 메일 전송
                send_request_mail(form, profile, request)
    
    is_waiting = CoffeeChat.objects.filter(user=request.user, profile=profile, status='WAITING').exists()
    waiting_requests = CoffeeChat.objects.filter(profile=profile, status='WAITING').count()
    is_limited = waiting_requests >= 2 or profile.count >= 2
    is_ongoing = CoffeeChat.objects.filter(user=request.user, profile=profile, status='ONGOING').exists()
    is_completed = CoffeeChat.objects.filter(user=request.user, profile=profile, status='COMPLETED').exists()
    hashtags = profile.hashtags.all()
    requests = CoffeeChat.objects.filter(profile=profile)

    scraps = Scrap.objects.filter(user=request.user, profile=profile)
    if scraps:
        bookmarked = True
    else:
        bookmarked = False

    for req in requests:
        req.existing_review = hasattr(req, 'review')


    ctx = {
        'profile': profile,
        'profile_requests': profile_requests,
        'is_waiting': is_waiting,
        'is_limited': is_limited,
        'is_ongoing': is_ongoing,
        'is_completed': is_completed,
        'has_pending_request': has_pending_request,
        'hashtags': hashtags,
        'requests': requests,
        'requestContent': CoffeechatRequestForm,
        'reviews': reviews,
        'profile_status': profile.profile_status,
        'user_has_profile': Profile.objects.filter(user=request.user).exists(),
        'existing_review': Review.objects.filter(
            user=request.user,
            coffeechat_request__profile=profile
        ).exists(),
        'bookmarked': bookmarked,
    }
    return render(request, 'coffeechat/detail.html', ctx)




@login_required
def coffeechat_request(request, post_id):
    coffeechat = get_object_or_404(Profile, pk=post_id)
    chat_request = CoffeeChat()
    chat_request.profile = coffeechat
    chat_request.user = request.user
      
    return redirect('coffeechat:coffeechat_detail', pk=coffeechat.pk)

@login_required
@require_POST
def accept_request(request, request_id):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({"error": "AJAX request required"}, status=400)

    coffeechat_request = get_object_or_404(CoffeeChat, id=request_id)
    if request.user != coffeechat_request.profile.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    agree = informationAgree()
    agree.coffeechat_request = coffeechat_request
    agree.date = timezone.now()
    agree.user = coffeechat_request.profile.user
    agree.is_agree = True

    inp = WayToContect(request.POST)
    if inp.is_valid():
        way = inp.cleaned_data['way']

    coffeechat_request.status = 'ONGOING'
    coffeechat_request.accepted_at = timezone.now()
    coffeechat_request.save()

    profile = coffeechat_request.profile
    profile.count += 1
    profile.save()

    # 양쪽 사용자를 위한 메모 생성
    from apps.coffeechat.models import Memo  # 상단에 import 추가 필요

    # 신청자(후배)를 위한 메모 생성
    Memo.objects.create(
        coffeeChatRequest=coffeechat_request,  # 올바른 필드명으로 수정
        user=coffeechat_request.user,
        content=""
    )

    # # 수락자(선배)를 위한 메모 생성
    # Memo.objects.create(
    #     coffeeChatRequest=coffeechat_request,  # 올바른 필드명으로 수정
    #     user=coffeechat_request.profile.user,
    #     content=""
    # )

    return send_accept_mail(coffeechat_request, profile, request)


@login_required
@require_POST
def reject_request(request, request_id):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({"error": "AJAX request required"}, status=400)

    coffeechat_request = get_object_or_404(CoffeeChat, id=request_id)
    if request.user != coffeechat_request.profile.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    coffeechat_request.status = "REJECTED"
    coffeechat_request.save()

    profile = coffeechat_request.profile
    return send_reject_mail(coffeechat_request, profile, request)


@login_required
def update(req, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if req.method == "POST":
        form = CoffeeChatForm(req.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = req.user
            profile.content = form.cleaned_data['content']
            profile.profile_status = form.cleaned_data['profile_status']
            profile.save()
            
            hashtags = json.loads(form.cleaned_data['hashtags'])
            hashtag_objects = []
            for tag in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(name=tag)
                hashtag_objects.append(hashtag)
            profile.hashtags.set(hashtag_objects)
            
            return redirect('coffeechat:coffeechat_detail', pk=profile.pk)
    else:
        form = CoffeeChatForm(instance=profile)
        initial_hashtags = json.dumps([tag.name for tag in profile.hashtags.all()])
        form.fields['hashtags'].initial = initial_hashtags
        form.fields['content'].initial = profile.content
        form.fields['profile_status'].initial = profile.profile_status

    return render(req, 'coffeechat/chatedit.html', {'form': form, 'profile': profile})

@login_required
def delete(req, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if req.method == "POST":
        profile.delete()
        return redirect('coffeechat:main')
    return render(req, 'coffeechat/delete.html', {'profile': profile})

def howto(request):  
    return render(request, 'coffeechat/howto.html')

def how_received(request):  
    return render(request, 'coffeechat/how_received.html')

@login_required
def cohort_profiles(request, cohort):
    profiles = Profile.objects.filter(user__cohort=cohort)
    return render(request, 'coffeechat/cohort_profiles.html', {'profiles': profiles, 'cohort': cohort})

@login_required
def bookmark_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    user = request.user

    # Scrap 객체 필터링
    scraps = Scrap.objects.filter(user=user, profile=profile)

    if scraps.exists():  # QuerySet의 값이 존재하는지 확인
        scraps.delete()  # 삭제
        bookmarked = False
        print("Scrap deleted.")
    else:
        # 새 Scrap 객체 생성
        scrap = Scrap.objects.create(user=user, profile=profile)
        bookmarked = True
        print(f"Scrap added by user: {scrap.user.username}")

    # JSON 응답 반환
    return JsonResponse({'bookmarked': bookmarked})


@login_required
def toggle_visibility(request, profile_id):
    profile = get_object_or_404(Profile, pk=profile_id, user=request.user)