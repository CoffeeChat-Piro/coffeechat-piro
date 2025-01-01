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
from apps.coffeechat.forms import WayToContect


# 프로젝트 내 모듈
from .models import CoffeeChat, Hashtag, CoffeeChatRequest, Review, CustomUser, informationAgree
from .forms import CoffeeChatForm, ReviewForm, CoffeechatRequestForm

User = get_user_model()
@login_required
def home(request):
    query = request.GET.get('search')
    profile_status_filter = request.GET.get('status')  # 프로필 상태값 필터 추가

    profiles = CoffeeChat.objects.all()

    if query:
        profiles = profiles.filter(
            Q(hashtags__name__icontains=query) |
            Q(receiver__username__icontains=query)
        ).distinct()

    if profile_status_filter:
        profiles = profiles.filter(profile_status=profile_status_filter)  # 프로필 상태값 필터 적용

    context = {
        "profiles": profiles
    }
    return render(request, 'coffeechat/home.html', context)

@login_required
def create(req):
    # 현재 사용자가 이미 프로필을 가지고 있는지 확인
    existing_profile = CoffeeChat.objects.filter(receiver=req.user).first()
    if existing_profile:
        return redirect('coffeechat:coffeechat_detail', pk=existing_profile.pk)  # 이미 존재하면 자신의 detail 페이지로 리디렉션

    if req.method == "POST": #생성 후
        form = CoffeeChatForm(req.POST)
        if form.is_valid():
            coffeechat = form.save(commit=False)
            coffeechat.receiver = req.user
            coffeechat.count = 0  # count 기본값 설정
            coffeechat.content = form.cleaned_data['content']
            coffeechat.profile_status = form.cleaned_data['profile_status']
            coffeechat.save()
            
            # 해시태그 저장
            hashtags = form.cleaned_data['hashtags']
            hashtag_list = json.loads(hashtags)
            hashtag_objects = []
            for tag in hashtag_list:
                hashtag, created = Hashtag.objects.get_or_create(name=tag)
                hashtag_objects.append(hashtag)
            coffeechat.hashtags.set(hashtag_objects)
            
            coffeechat.save()
            return redirect('coffeechat:coffeechat_detail', pk=coffeechat.pk)
    else: #생성 전(GET)
        form = CoffeeChatForm()
    ctx = {
        'form': form
    }
    return render(req, 'coffeechat/create.html', ctx)

@csrf_protect
@login_required
def create_review(request, coffeechat_request_id):
    coffeechat_request = get_object_or_404(CoffeeChatRequest, id=coffeechat_request_id)

    # 요청을 보낸 사용자가 요청을 받은 사용자인 경우 접근 금지
    if request.user != coffeechat_request.user:
        return HttpResponseForbidden("리뷰 작성 권한이 없습니다.")

    # 이미 리뷰가 존재하는지 확인
    if hasattr(coffeechat_request, 'review'):
        return render(request, 'coffeechat/review_form.html', {
            'error_message': '이미 이 요청에 대한 리뷰가 작성되었습니다.'
        })

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.coffeechat_request = coffeechat_request
            review.save()
            
            # 리뷰 작성 시 profile.count 증가
            coffeechat = coffeechat_request.coffeechat
            coffeechat.count += 1
            coffeechat.save()

            return redirect('coffeechat:coffeechat_detail', pk=coffeechat_request.coffeechat.pk)
        else:
            return render(request, 'coffeechat/review_form.html', {
                'form': form,
                'error_message': '폼이 유효하지 않습니다.'
            })
    else:
        form = ReviewForm()
    return render(request, 'coffeechat/review_form.html', {'form': form})


def detail(request, pk):
    profile = CoffeeChat.objects.get(pk=pk)
    coffeechat_requests = CoffeeChatRequest.objects.filter(coffeechat=profile)
    reviews = Review.objects.filter(coffeechat_request__coffeechat=profile)

    # 현재 사용자가 프로필 소유자로부터 커피챗 요청을 받았는지 확인
    has_pending_request = CoffeeChatRequest.objects.filter(
        user=profile.receiver,  # 프로필 소유자가 요청을 보낸 사람
        coffeechat__receiver=request.user,  # 현재 로그인한 사용자가 이 요청을 받은 사람
        status='WAITING'
    ).exists()

    if request.method == "POST" and request.user != profile.receiver:
        existing_request = False
        if not existing_request:
            start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            daily_requests = CoffeeChatRequest.objects.filter(
                coffeechat__receiver=profile.receiver,
                created_at__range=(start_of_day, end_of_day),
                status='WAITING'
            ).count()

            if daily_requests < 5:
                form = CoffeechatRequestForm(request.POST)
                if form.is_valid():
                    message = form.cleaned_data['requestContent']

                    #메일 전송
                    subject = "PiroTime: 커피챗 신청이 왔습니다!"
                    content = f"{profile.receiver}님! 작성하신 커피챗 프로필에 요청한 사람이 있습니다! 아래 링크로 들어와 확인해 보세요."
                    sending_mail(profile.receiver, request.user, subject, content, message)

                    #리쿼스트 생성


                    CoffeeChatRequest.objects.create(
                        user=request.user,
                        coffeechat=profile,
                        status='WAITING',
                        letterToSenior=message
                    )


                    subject = "PiroTime: 커피챗 신청이 왔습니다!"
                    content = f"{profile.receiver}님! 작성하신 커피챗 프로필에 요청한 사람이 있습니다! 아래 링크로 들어와 확인해 보세요."
                    sending_mail(profile.receiver, request.user, subject, content, message)


            else:
                profile.status = 'LIMITED'
                profile.save()

    
    is_waiting = CoffeeChatRequest.objects.filter(user=request.user, coffeechat=profile, status='WAITING').exists()
    waiting_requests = CoffeeChatRequest.objects.filter(coffeechat__receiver=profile.receiver, status='WAITING').count()
    is_limited = waiting_requests >= 2 and not is_waiting
    hashtags = profile.hashtags.all()
    requests = CoffeeChatRequest.objects.filter(coffeechat=profile)
    profile_status = profile.profile_status      #프로필 상태값 추가

    # 요청마다 리뷰가 있는지 확인하여 request 객체에 속성 추가
    for req in requests:
        req.existing_review = hasattr(req, 'review')

    ctx = {
        'profile': profile,
        'is_waiting': is_waiting,
        'is_limited': is_limited,
        'has_pending_request': has_pending_request,  # 새로 추가된 컨텍스트 변수
        'hashtags': hashtags,
        'requests': requests,
        'requestContent': CoffeechatRequestForm,
        'reviews': reviews,  # 해당 사용자의 리뷰 추가
        'profile_status': profile_status,
    }
    return render(request, 'coffeechat/detail.html', ctx)

@login_required
def coffeechat_request(request, post_id):
    coffeechat = CoffeeChat.objects.get(post_id)
    receiver = coffeechat.receiver
    chat_request = CoffeeChatRequest()

    chat_request.coffeechat = coffeechat
    chat_request.user = request.user

from django.views.decorators.http import require_POST

@login_required
@require_POST
def accept_request(request, request_id):
    # AJAX 요청인지 확인
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({"error": "AJAX request required"}, status=400)

    coffeechat_request = get_object_or_404(CoffeeChatRequest, id=request_id)
    if request.user != coffeechat_request.coffeechat.receiver:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    print('accept 1+++++++++++++++')
    agree = informationAgree()
    agree.coffeechat_request = coffeechat_request
    agree.date = timezone.now()
    agree.user = coffeechat_request.coffeechat.receiver
    agree.is_agree = True

    inp = WayToContect(request.POST)
    if inp.is_valid():
        way = inp.cleaned_data['way']
        print(way)

    print('accept 2+++++++++++++++')

    coffeechat_request.status = 'ACCEPTED'
    coffeechat_request.save()

    coffeechat = coffeechat_request.coffeechat
    coffeechat.count += 1
    coffeechat.save()

    subject = f"PiroTime: {request.user}님이 커피챗 요청을 수락했습니다!"
    content = f"{coffeechat_request.user}님! 요청하신 커피챗 요청이 수락되었습니다! 아래에 있는 연락처로 연락해보세요!"
    message = ""

    try:
        sending_mail_info(coffeechat.receiver, coffeechat_request.user, subject, content, message)
    except Exception as e:
        return JsonResponse({"error": "메일을 보내는 중 문제가 발생했습니다."}, status=503)

    print('accept 3+++++++++++++++')

    return JsonResponse({"status": "accepted"})

@login_required
@require_POST
def reject_request(request, request_id):
    # AJAX 요청인지 확인
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({"error": "AJAX request required"}, status=400)

    coffeechat_request = get_object_or_404(CoffeeChatRequest, id=request_id)
    if request.user != coffeechat_request.coffeechat.receiver:
        return JsonResponse({"error": "Unauthorized"}, status=403)

    coffeechat_request.status = "REJECTED"
    coffeechat_request.save()

    coffeechat = coffeechat_request.coffeechat
    subject = f"PiroTime: {request.user}님이 커피챗 요청을 거절하셨습니다!"
    message = f"{coffeechat_request.user}님! 선배님의 개인 사정으로 인해 커피챗 요청이 거절되었습니다. 다른 선배님과의 커피챗은 어떠하신가요?"
    content = ""

    try:
        sending_mail(coffeechat.receiver, coffeechat_request.user, subject, content, message)
    except Exception as e:
        return JsonResponse({"error": "메일을 보내는 중 문제가 발생했습니다."}, status=503)

    return JsonResponse({"status": "rejected"})

@login_required
def update(req, pk):
    profile = CoffeeChat.objects.get(pk=pk)
    if req.method == "POST": # 수정 후
        form = CoffeeChatForm(req.POST, instance=profile)
        if form.is_valid():
            coffeechat = form.save(commit=False)
            coffeechat.receiver = req.user
            coffeechat.count = 0  # count 필드에 기본값 설정
            coffeechat.content = form.cleaned_data['content']
            coffeechat.profile_status = form.cleaned_data['profile_status']  # profile_status 수정
            coffeechat.save()
            
            # 해시태그 저장
            hashtags = form.cleaned_data['hashtags']
            hashtag_list = json.loads(hashtags)
            hashtag_objects = []
            for tag in hashtag_list:
                hashtag, created = Hashtag.objects.get_or_create(name=tag)
                hashtag_objects.append(hashtag)
            coffeechat.hashtags.set(hashtag_objects)
            
            coffeechat.save()
            return redirect('coffeechat:coffeechat_detail', pk=profile.pk)
    else: # 수정 전(위한 load, GET)
        form = CoffeeChatForm(instance=profile)
        # 수정을 위해서 기존 콘텐츠와 해시태그 로드(JSON)
        initial_hashtags = json.dumps([{'value': hashtag.name} for hashtag in profile.hashtags.all()])
        form.fields['hashtags'].initial = initial_hashtags
        form.fields['content'].initial = profile.content
        form.fields['profile_status'].initial = profile.profile_status  # profile_status 초기값 설정

    ctx = {
        'form': form,
        'profile': profile
    }
    return render(req, 'coffeechat/update.html', ctx)

@login_required
def delete(req, pk):
    profile = CoffeeChat.objects.get(pk=pk)
    if req.method == "POST":
        profile.delete()
        return redirect('coffeechat:coffeechat_home')
    ctx = {
        'profile': profile
    }
    return render(req, 'coffeechat/delete.html', ctx)


def generate_email_content(sender, receiver):
    subject = "PiroTime: 커피쳇 신청이 왔습니다!"
    message = f"{sender.username}님으로 부터 협력 제안이 왔습니다. PiroTime에 접속해서 내용을 확인하세요!"
    from_email = 'pirotimeofficial@gmail.com'
    recipient_list = [receiver.email]
    return subject, message, from_email, recipient_list

def sending_mail(receiver, sender, subject, content, message):

    subject = subject
    content = content

    from_email = 'pirotimeofficial@gmail.com'
    recipient_list = [receiver.email]
    

    html_message = render_to_string(
        "corboard/message.html",
        {"sender": sender.username,
         "receiver": receiver.username,
         "content": content,
         "message": message},

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

def format_phone_number(phone_number):
    # 만약 전화번호가 '+82'로 시작하면
    if phone_number.startswith('+82'):
        # '+82'를 제거하고 앞에 '0'을 붙임
        return '0' + phone_number[3:]
    return phone_number  # 다른 경우는 그대로 반환

def sending_mail_info(receiver, sender, subject, content, message):

    subject = subject
    content = content

    from_email = 'pirotimeofficial@gmail.com'
    recipient_list = [sender.email]
    mail = receiver.email
    phoneNumber = format_phone_number(receiver.phone_number)

    html_message = render_to_string(
        "corboard/message_accept_coffeechat.html",
        {"sender": sender.username,
         "receiver": receiver.username,
         "content": content,
         "message": message,
         "mail": mail,
         "phoneNumber": phoneNumber,
         },

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

def cohort_profiles(request, cohort):
    profiles = CustomUser.objects.filter(cohort=cohort)
    return render(request, 'coffeechat/cohort_profiles.html', {'profiles': profiles, 'cohort': cohort})

@login_required
def bookmark_profile(request, pk):
    profile = get_object_or_404(CoffeeChat, pk=pk)
    if request.user in profile.bookmarks.all():
        profile.bookmarks.remove(request.user)
        bookmarked = False
    else:
        profile.bookmarks.add(request.user)
        bookmarked = True
    print(bookmarked)
    return JsonResponse({'bookmarked': bookmarked})

@login_required
def toggle_visibility(request, profile_id):
    profile = get_object_or_404(CoffeeChat, pk=profile_id, receiver=request.user)
    profile.is_public = not profile.is_public  # 현재 상태를 반전시킴
    profile.save()
    return redirect('coffeechat:coffeechat_detail', pk=profile_id)