# 표준 라이브러리
import json
from datetime import timedelta

# Django 모듈
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from apps.coffeechat.forms import WayToContect

# 프로젝트 내 모듈
from .models import Profile, Hashtag, CoffeeChat, Review, User, informationAgree
from .forms import CoffeeChatForm, ReviewForm, CoffeechatRequestForm

User = get_user_model()

@login_required
def home(request):
    query = request.GET.get('search')
    profile_status_filter = request.GET.get('status')

    profiles = Profile.objects.all()

    if query:
        profiles = profiles.filter(
            Q(hashtags__name__icontains=query) |
            Q(user__username__icontains=query)
        ).distinct()

    if profile_status_filter:
        profiles = profiles.filter(profile_status=profile_status_filter)
    
    user_profile = Profile.objects.filter(user=request.user).first()
   
    context = {
        "profiles": profiles,
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
            
            profile = coffeechat_request.profile
            profile.count += 1
            profile.save()

            return redirect('coffeechat:coffeechat_detail', pk=coffeechat_request.profile.pk)
    else:
        form = ReviewForm()
    return render(request, 'coffeechat/review_form.html', {'form': form})

def detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    coffeechat_requests = CoffeeChat.objects.filter(profile=profile)
    reviews = Review.objects.filter(coffeechat_request__profile=profile)

    has_pending_request = CoffeeChat.objects.filter(
        user=profile.user,
        profile__user=request.user,
        status='WAITING'
    ).exists()

    if request.method == "POST" and request.user != profile.user:
        waiting_requests = CoffeeChat.objects.filter(
            profile=profile,
            status__in=['WAITING', 'ONGOING', 'ACCEPTED', 'COMPLETED']
        ).count()

        if waiting_requests < 2:
            form = CoffeechatRequestForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data['requestContent']

                subject = "PiroTime: 커피챗 신청이 왔습니다!"
                content = f"{profile.user}님! 작성하신 커피챗 프로필에 요청한 사람이 있습니다! 아래 링크로 들어와 확인해 보세요."
                sending_mail(profile.user, request.user, subject, content, message)

                CoffeeChat.objects.create(
                    user=request.user,
                    profile=profile,
                    status='WAITING',
                    letterToSenior=message
                )
        else:
            profile.profile_status = 'LIMITED'
            profile.save()
    
    is_waiting = CoffeeChat.objects.filter(user=request.user, profile=profile, status='WAITING').exists()
    waiting_requests = CoffeeChat.objects.filter(profile=profile, status='WAITING').count()
    is_limited = waiting_requests >= 2 and not is_waiting
    is_ongoing = CoffeeChat.objects.filter(user=request.user, profile=profile, status='ONGOING').exists()
    is_completed = CoffeeChat.objects.filter(user=request.user, profile=profile, status='COMPLETED').exists()
    hashtags = profile.hashtags.all()
    requests = CoffeeChat.objects.filter(profile=profile)

    for req in requests:
        req.existing_review = hasattr(req, 'review')

    ctx = {
        'profile': profile,
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
    }
    return render(request, 'coffeechat/detail.html', ctx)

@login_required
def coffeechat_request(request, post_id):
    coffeechat = get_object_or_404(Profile, pk=post_id)
    receiver = coffeechat.user
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
    coffeechat_request.save()

    profile = coffeechat_request.profile
    profile.count += 1
    profile.save()

    subject = f"PiroTime: {request.user}님이 커피챗 요청을 수락했습니다!"
    content = f"{coffeechat_request.user}님! 요청하신 커피챗 요청이 수락되었습니다! 아래에 있는 연락처로 연락해보세요!"
    message = ""

    try:
        sending_mail_info(profile.user, coffeechat_request.user, subject, content, message)
    except Exception as e:
        return JsonResponse({"error": "메일을 보내는 중 문제가 발생했습니다."}, status=503)

    return JsonResponse({"status": "accepted"})

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
    subject = f"PiroTime: {request.user}님이 커피챗 요청을 거절하셨습니다!"
    message = f"{coffeechat_request.user}님! 선배님의 개인 사정으로 인해 커피챗 요청이 거절되었습니다. 다른 선배님과의 커피챗은 어떠하신가요?"
    content = ""

    try:
        sending_mail(profile.user, coffeechat_request.user, subject, content, message)
    except Exception as e:
        return JsonResponse({"error": "메일을 보내는 중 문제가 발생했습니다."}, status=503)

    return JsonResponse({"status": "rejected"})

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

def generate_email_content(sender, receiver):
    subject = "PiroTime: 커피챗 신청이 왔습니다!"
    message = f"{sender.username}님으로 부터 협력 제안이 왔습니다. PiroTime에 접속해서 내용을 확인하세요!"
    from_email = 'pirotimeofficial@gmail.com'
    recipient_list = [receiver.email]
    return subject, message, from_email, recipient_list

def sending_mail(receiver, sender, subject, content, message):
    from_email = 'pirotimeofficial@gmail.com'
    recipient_list = [receiver.email]

    html_message = render_to_string(
        "coffeechat/message.html",
        {
            "sender": sender.username,
            "receiver": receiver.username,
            "content": content,
            "message": message
        }
    )
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
    )
    return True

def sending_mail_info(receiver, sender, subject, content, message):
    from_email = 'pirotimeofficial@gmail.com'
    recipient_list = [sender.email]
    mail = receiver.email

    html_message = render_to_string(
        "coffeechat/message_accept_coffeechat.html",
        {
            "sender": sender.username,
            "receiver": receiver.username,
            "content": content,
            "message": message,
            "mail": mail,
        }
    )
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
    )
    return True

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
    if request.user in profile.bookmarks.all():
        profile.bookmarks.remove(request.user)
        bookmarked = False
    else:
        profile.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})

@login_required
def toggle_visibility(request, profile_id):
    profile = get_object_or_404(Profile, pk=profile_id, user=request.user)