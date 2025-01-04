# Django 내장 모듈
import profile

from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# 프로젝트 내 모듈
from apps.accounts.models import User
from apps.accounts.forms import CustomUserChangeForm
# from apps.review.models import Review, Comment as ReviewComment
# from apps.corboard.models import Corboard, Comment as CorboardComment
# from apps.trend.models import Trend, Comment as TrendComment
from apps.coffeechat.models import Profile, CoffeeChat, Scrap, Memo
from apps.coffeechat.forms import WayToContect
from django.contrib.auth.hashers import check_password

# 프로필 보기 뷰
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'mypage/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        return context

# 프로필 수정 뷰
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'mypage/profile_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('mypage:profile') + '?success=True'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        print("Form is valid, redirecting to success_url")
        response = super().form_valid(form)
        return response

    def form_invalid(self, form):
        print("Form is invalid, reloading the form")
        print(form.errors)
        messages.error(self.request, '오류가 발생했습니다. 입력 내용을 다시 확인해 주세요.')
        return super().form_invalid(form)

# AJAX
class ActivitiesAjaxView(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        filter_type = request.GET.get('filter', 'my_posts')
        category = request.GET.get('category', 'all')
        user_id = request.GET.get('user_id', None)

        # 특정 사용자 글 필터링하기 위해 user_id 사용
        if user_id:
            target_user = get_object_or_404(User, id=user_id)
        else:
            target_user = request.user

        # 커피챗 필터링
        if filter_type == 'coffeechat':
            if category == 'requests_sent':
                requests_sent = CoffeeChat.objects.filter(user=target_user, status='WAITING')
                data = [{
                    'sender': request.user.username,
                    'receiver': request.profile.user.username,
                    'job': request.profile.job,
                    'created_at': request.created_at.isoformat(),
                    'status': request.get_status_display(),
                    'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[request.profile.id]),
                    'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.profile.user.id]),
                } for request in requests_sent]
                print("Debug Data for requests_sent:", data)
                return JsonResponse({'requests_sent': data})

            elif category == 'requests_received':
                requests_received = CoffeeChat.objects.filter(coffeechat__receiver=target_user, status='WAITING')
                data = []
                debug_data = []

                for request in requests_received:
                    sender_username = request.user.username
                    sender_id = request.user.id
                    receiver_username = request.profile.user.username if request.profile.user else 'Unknown'
                    job = request.profile.job
                    detail_url = reverse_lazy('coffeechat:coffeechat_detail', args=[request.profile.id])
                    cohort = request.user.cohort  # 신청한 사람의 기수

                    # 디버깅 정보 리스트
                    debug_data.append({
                        'request_id': request.id,
                        'coffeechat_id': request.profile.id,
                        'sender_username': sender_username,
                        'receiver_username': receiver_username,
                        'job': job,
                        'cohort': cohort,  # 추가된 부분
                        'detail_url': detail_url,
                        'status': request.status,
                        'receiver_id': request.profile.user.id if request.profile.user else 'None',
                        'sender_id': request.user.id,
                        'letter_to_senior': request.letterToSenior,  # 추가된 부분
                        
                    })


                    data.append({
                        'sender': sender_username,
                        'sender_id': sender_id,
                        'receiver': receiver_username,
                        'job': job,
                        'cohort': cohort,  # 추가된 부분
                        'created_at': request.created_at.isoformat(),
                        'status': request.get_status_display(),
                        'detail_url': detail_url,
                        'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.profile.user.id if request.profile.user else '']),
                        'accept_url': reverse_lazy('coffeechat:accept_request', args=[request.id]),
                        'reject_url': reverse_lazy('coffeechat:reject_request', args=[request.id]),
                        'letter_to_senior': request.letterToSenior,  # 추가된 부분
                    })

                # 디버깅 정보를 출력
                print("Debug Data for requests_received:", debug_data)

                return JsonResponse({'requests_received': data})

            elif category == 'bookmarked':
                bookmarked_coffeechats = Profile.objects.filter(bookmarks=target_user)
                data = [{
                    'receiver': coffeechat.user.username,
                    'job': coffeechat.job,
                    'created_at': coffeechat.created_at.isoformat(),
                    'content': coffeechat.content,
                    'hashtags': [hashtag.name for hashtag in coffeechat.hashtags.all()],
                    'bookmarked': True,
                    'coffeechat_bookmark_profile': reverse_lazy('mypage:coffeechat_bookmark_profile', args=[coffeechat.id]),
                    'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[coffeechat.id]),
                    'profile_read_url': reverse_lazy('mypage:profile_read', args=[coffeechat.user.id if coffeechat.user else '']),
                } for coffeechat in bookmarked_coffeechats]
                return JsonResponse({'bookmarked_coffeechats': data})
            
            elif category == 'history':
                accepted_requests = CoffeeChat.objects.filter(user=target_user, status='ACCEPTED')
                data = [{
                    'sender': request.user.username,
                    'receiver': request.profile.user.username,
                    'job': request.profile.job,
                    'created_at': request.created_at.isoformat(),
                    'status': request.get_status_display(),
                    'hashtags': [hashtag.name for hashtag in request.profile.hashtags.all()],
                    'review': {
                        'rating': request.review.rating if hasattr(request, 'review') else None,
                        'content': request.review.content if hasattr(request, 'review') else None,
                        'created_at': request.review.created_at.isoformat() if hasattr(request, 'review') else None,
                    } if hasattr(request, 'review') else None,
                    'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[request.profile.id]),
                    'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.profile.user.id]),
                    'review_exists': True if hasattr(request, 'review') else False,
                } for request in accepted_requests]
                return JsonResponse({'accepted_requests': data})

        # 내 정보 보기
        elif filter_type == 'profile_info':
            user = target_user
            data = {
                'username': user.username,
                'email': user.email,
                'profile_image': user.profile_image.url if user.profile_image else None,
                'cohort': user.cohort,
                'intro': user.intro,
            }
            return JsonResponse(data)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'mypage/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user

        # 랜덤으로 출력할 사진 리스트
        image_files = ['back.png', 'back1.png', 'back2.png']
        context['image_files'] = image_files

        return context

import random

def profile_read(request, user_id):
    User = get_user_model()
    user_profile = get_object_or_404(User, pk=user_id)
    
    # 랜덤으로 출력할 사진 리스트
    image_files = ['back.png', 'back1.png', 'back2.png']
    random_image = random.choice(image_files)

    return render(request, 'mypage/profile_read.html', {
        'profile_user': user_profile,
        'random_image': random_image,
    })

@login_required
def coffeechat_bookmark_profile(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if request.user in profile.bookmarks.all():
        profile.bookmarks.remove(request.user)
        bookmarked = False
    else:
        profile.bookmarks.add(request.user)
        bookmarked = True

    return JsonResponse({'bookmarked': bookmarked})

@login_required
def profile_modal_view(request):
    user_id = request.GET.get('user_id')
    profile_user = get_object_or_404(User, id=user_id)

    image_files = ['back.png', 'back1.png', 'back2.png']
    random_image = random.choice(image_files)

    context = {
        'profile_user': profile_user,
        'random_image': random_image,
    }

    # 서버 로그에 출력
    print(f"Random Image URL: /static/images/{random_image}")

    return render(request, 'mypage/profile_modal.html', context)

@login_required
def password_change(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # 현재 사용자
        user = request.user

        # 기존 비밀번호 확인
        if not check_password(current_password, user.password):     #내장함수: 비밀번호 검증
            messages.error(request, "현재 비밀번호가 일치하지 않습니다.")
            return render(request, 'mypage/password_change.html')

        # 새로운 비밀번호와 확인 비밀번호가 일치하지 않는 경우
        if new_password != confirm_password:
            messages.error(request, "새 비밀번호와 확인 비밀번호가 일치하지 않습니다.")
            return render(request, 'mypage/password_change.html')

        # 비밀번호 변경
        user.set_password(new_password)
        user.save()

        messages.success(request, "비밀번호가 성공적으로 변경되었습니다.")
        return redirect('password')  # 성공 후 리디렉션

    return render(request, 'mypage/password_change.html')

from django.shortcuts import render

@login_required
def coffeechat_received(request):
    if request.method == "GET":
        # 현재 로그인된 사용자 가져오기
        current_user = request.user

        # 요청한 사용자와 상태가 'WAITING'인 CoffeeChat 필터링
        chats = CoffeeChat.objects.filter(profile=current_user.profile, status='WAITING')

        # 결과 데이터를 템플릿에 전달
        context = {
            "chats": [
                {
                    "id": chat.id,
                    "name": chat.user.username,
                    "cohort": chat.user.cohort,
                    "created_at": chat.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for chat in chats
            ]
        }

        # 화면 출력
        return render(request, "coffeechat/received.html", context)

    # 잘못된 요청 처리
    return render(request, "coffeechat/error.html", {"message": "Invalid request method."}, status=400)

@login_required
def coffeechat_requested(request):
    if request.method == "GET":
        # 현재 로그인된 사용자 가져오기
        current_user = request.user

        # 요청한 사용자와 상태가 'WAITING'인 CoffeeChat 필터링
        chats = CoffeeChat.objects.filter(user=current_user, status='WAITING')

        # 결과 데이터를 템플릿에 전달
        context = {
            "chats": [
                {
                    "id": chat.id,
                    "name": chat.profile.user.username,
                    "cohort": chat.profile.user.cohort,
                    "created_at": chat.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for chat in chats
            ]
        }

        # 화면 출력
        return render(request, "coffeechat/requested.html", context)

    # 잘못된 요청 처리
    return render(request, "coffeechat/error.html", {"message": "Invalid request method."}, status=400)

@login_required
def coffeechat_in_progress(request):
    if request.method == "GET":
        # 현재 로그인된 사용자 가져오기
        current_user = request.user

        # 요청한 사용자와 상태가 'ONGOING'인 CoffeeChat 필터링
        chats = CoffeeChat.objects.filter(user__in=[current_user, current_user.profile.user], status='ONGOING')

        # 결과 데이터를 템플릿에 전달
        context = {
            "chats": [
                {
                    "id": chat.id,
                    "name": chat.profile.user.username,
                    "cohort": chat.profile.user.cohort,
                    "created_at": chat.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    "memo": chat.memo.id,
                }
                for chat in chats
            ]
        }

        # 화면 출력
        return render(request, "coffeechat/in_progress.html", context)

    # 잘못된 요청 처리
    return render(request, "coffeechat/error.html", {"message": "Invalid request method."}, status=400)

@login_required
def coffeechat_completed(request):
    if request.method == "GET":
        # 현재 로그인된 사용자 가져오기
        current_user = request.user

        # 요청한 사용자와 상태가 'COMPLETED'인 CoffeeChat 필터링
        chats = CoffeeChat.objects.filter(user__in=[current_user, current_user.profile.user], status='COMPLETED')

        # 결과 데이터를 템플릿에 전달
        context = {
            "chats": [
                {
                    "id": chat.id,
                    "name": chat.profile.user.username,
                    "cohort": chat.profile.user.cohort,
                    "created_at": chat.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                }
                for chat in chats
            ]
        }

        # 화면에 출력 (템플릿 경로를 변경해야 함)
        return render(request, "coffeechat/completed.html", context)

    # 잘못된 요청 처리
    return render(request, "coffeechat/error.html", {"message": "Invalid request method."}, status=400)
@login_required
def memo(request, pk):

    saved_memo = get_object_or_404(Memo, pk=pk, user=request.user)

    data = [
        {
            "content": saved_memo.content,
            "created_at": saved_memo.updated_at,
        }
    ]

    if request.method == "POST":
        # 폼 데이터에서 내용 가져오기
        content = request.POST.get("content", "").strip()


        # 메모 내용 저장: 공백이어도 좋다.
        saved_memo.content = content
        saved_memo.save()
        messages.success(request, "메모가 성공적으로 저장되었습니다.")
        return redirect('coffeechat_memo', pk=saved_memo.pk)

    return render(request, 'memo/memo_form.html', {'memo': saved_memo})

@login_required
def scraped(request, pk):
    # Scrap 객체 가져오기
    scraped_data = get_list_or_404(Scrap, pk=pk, user=request.user)

    # 관련된 Profile 가져오기
    profile = scraped_data.profile

    # 템플릿에 데이터 전달
    return render(request, 'scraps/profile_detail.html', {'profile': profile})
