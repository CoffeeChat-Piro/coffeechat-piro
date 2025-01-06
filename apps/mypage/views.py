# Django 내장 모듈
import os
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
import random

# 프로젝트 내 모듈
from apps import coffeechat
from apps.accounts.models import User
from apps.accounts.forms import CustomUserChangeForm
# from apps.review.models import Review, Comment as ReviewComment
# from apps.corboard.models import Corboard, Comment as CorboardComment
# from apps.trend.models import Trend, Comment as TrendComment
from apps.coffeechat.models import Profile, CoffeeChat, Scrap, Memo, Review
from apps.coffeechat.forms import WayToContect
from django.contrib.auth.hashers import check_password
from django.contrib.auth import update_session_auth_hash 

# 마이페이지 보기 뷰
class mypageView(LoginRequiredMixin, TemplateView):
    template_name = 'mypage/mypage.html'

    def get_context_data(self, **kwargs):

        # 현재 사용자와 관련된 모든 Scrap 객체 가져오기
        scraped_data = Scrap.objects.filter(user=self.request.user)

        # Scrap 객체에서 profile 필드를 리스트로 추출
        profiles = [scrap.profile for scrap in scraped_data]

        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profiles'] = profiles
        return context

# 마이페이지 수정 뷰
class mypageEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = 'mypage/modifyinfo.html'
    
    def get_success_url(self):
        return reverse_lazy('mypage:profile') + '?success=True'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save(commit=False)
        
        # 이미지 삭제 요청 확인 (문자열 'true'로 전송됨)
        delete_profile = self.request.POST.get('delete_profile_image') == 'true'
        has_new_image = 'profile_image' in self.request.FILES
        
        # 이미지 삭제 처리
        if delete_profile and user.profile_image:
            try:
                if hasattr(user.profile_image, 'path'):
                    if os.path.exists(user.profile_image.path):
                        os.remove(user.profile_image.path)
                user.profile_image = None
            except Exception as e:
                print(f"Error deleting image: {e}")
                
        # 새 이미지 업로드 처리
        elif has_new_image:
            if user.profile_image:
                try:
                    if hasattr(user.profile_image, 'path'):
                        if os.path.exists(user.profile_image.path):
                            os.remove(user.profile_image.path)
                except Exception as e:
                    print(f"Error removing old image: {e}")
            user.profile_image = self.request.FILES['profile_image']
        
        user.save()
        messages.success(self.request, '회원정보가 성공적으로 수정되었습니다.')
        return super().form_valid(form)


    def form_invalid(self, form):
        print("Form is invalid, reloading the form")
        print(form.errors)
        messages.error(self.request, '오류가 발생했습니다. 입력 내용을 다시 확인해 주세요.')
        return super().form_invalid(form)


#프로필 보기.
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'mypage/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user

        # 랜덤으로 출력할 사진 리스트
        image_files = ['back.png', 'back1.png', 'back2.png']
        context['image_files'] = image_files

        return context


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

#비밀번호 변경
@login_required
def password_change(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # 현재 사용자
        user = request.user

        errors = {}

        # 기존 비밀번호 확인
        if not check_password(current_password, user.password):
            errors["current_password"] = "현재 비밀번호가 일치하지 않습니다."

        # 새로운 비밀번호와 확인 비밀번호가 일치하지 않는 경우
        if new_password != confirm_password:
            errors["confirm_password"] = "새 비밀번호와 확인 비밀번호가 일치하지 않습니다."

        if errors:
            return render(request, 'mypage/modifypwd.html', {"errors": errors})

        # 비밀번호 변경
        user.set_password(new_password)
        user.save()

        # 로그아웃 방지
        update_session_auth_hash(request, user)

        messages.success(request, "비밀번호가 성공적으로 변경되었습니다.")
        return redirect('mypage:profile')

    return render(request, 'mypage/modifypwd.html')

#받은 커피챗 조회
@login_required
def coffeechat_received(request):
    if request.method == "GET":
        # 현재 로그인된 사용자 가져오기
        current_user = request.user

        user_profile = Profile.objects.filter(user=current_user).first()

        if user_profile:
            # 요청한 사용자와 상태가 'WAITING'인 CoffeeChat 필터링
            chats = CoffeeChat.objects.filter(profile=user_profile, status='WAITING')

            # 결과 데이터를 템플릿에 전달
            context = {
                "chats": [
                    {
                        "id": chat.id,
                        "name": chat.user.username,
                        "cohort": chat.user.cohort,
                        "created_at": chat.created_at,
                        "letterToSenior": chat.letterToSenior,
                    }
                    for chat in chats
                ]
            }
        else:
            context = None

        # 화면 출력
        return render(request, "mypage/mychatpull.html", context)

    # 잘못된 요청 처리
    return render(request, "mypage/error.html", {"message": "Invalid request method."}, status=400)

#신청한 요청 조회
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
                    "created_at": chat.created_at,
                    "letterToSenior": chat.letterToSenior,
                }
                for chat in chats
            ]
        }

        # 화면 출력
        return render(request, "mypage/mychatpush.html", context)

    # 잘못된 요청 처리
    return render(request, "coffeechat/error.html", {"message": "Invalid request method."}, status=400)

#진행중인 커피챗
@login_required
def coffeechat_in_progress(request):
    if request.method == "GET":
        # 현재 로그인된 사용자 가져오기
        current_user = request.user

        # 진행중인 커피챗 모두 찾기
        chats = CoffeeChat.objects.filter(
            status='ONGOING'
        ).filter(
            user=current_user
        ) | CoffeeChat.objects.filter(
            status='ONGOING'
        ).filter(
            profile__user=current_user
        )

        chat_list = []
        for chat in chats:
            if chat.user == current_user:  # 내가 신청자인 경우
                other_user = chat.profile.user
            else:  # 내가 신청받은 사람인 경우
                other_user = chat.user

        context = {
            "chats": [
                {
                    "id": chat.id,
                    "name": other_user.username,
                    "cohort": other_user.cohort,
                    "accepted_at": chat.created_at,
                    "letterToSenior": chat.letterToSenior,
                    "memo_id": chat.memo.id if chat.user == current_user else False,
                    "is_requester": True if chat.user == current_user else False,
                }
                for chat in chats
            ]
        }
        
        return render(request, "mypage/mychating.html", context)

    return render(request, "coffeechat/error.html", {"message": "Invalid request method."}, status=400)

#완료된 커피챗 조회
@login_required
def coffeechat_completed(request):
    if request.method == "GET":
        current_user = request.user
        
        chats = CoffeeChat.objects.filter(
            status='COMPLETED'
        ).filter(
            user=current_user
        ) | CoffeeChat.objects.filter(
            status='COMPLETED'
        ).filter(
            profile__user=current_user
        )
        
        chat_list = []
        for chat in chats:
            if chat.user == current_user:  # 내가 신청자인 경우
                other_user = chat.profile.user
            else:  # 내가 신청받은 사람인 경우
                other_user = chat.user
        #
        #     memo = Memo.objects.filter(coffeeChatRequest=chat.id).first()
        #     review_done = Review.objects.filter(coffeechat_request=chat).exists()
        #
        #     chat_data = {
        #         "id": chat.id,
        #         "name": other_user.username,
        #         "cohort": other_user.cohort,
        #         "accepted_at": chat.accepted_at,
        #         "memo_id": memo.id if memo else None,
        #         "review_done": review_done,
        #         "is_requester": is_requester  # 신청자 여부 전달
        #     }
        #     chat_list.append(chat_data)
        #
        # context = {
        #     "chats": chat_list
        # }

        context = {
            "chats": [
                {
                    "id": chat.id,
                    "name": other_user.username,
                    "cohort": other_user.cohort,
                    "accepted_at": chat.created_at,
                    "memo_id": chat.memo.id if chat.user == current_user else False,
                    "review_done": True if Review.objects.filter(coffeechat_request=chat).exists() else False,
                    "is_requester": True if chat.user == current_user else False,
                }
                for chat in chats
            ]
        }
        
        return render(request, "mypage/mychatend.html", context)
    
    return render(request, "coffeechat/error.html", {"message": "Invalid request method."}, status=400)

@login_required
def coffeechat_to_complete(request, pk):
    coffeechat = get_object_or_404(CoffeeChat, pk=pk)

    if request.user == coffeechat.user or request.user == coffeechat.profile.user:
        coffeechat.status = 'COMPLETED'
        coffeechat.save()  # 변경 사항 저장
        
        coffeechat_request = get_object_or_404(CoffeeChat, id=pk)
        profile = coffeechat_request.profile
        profile.count -= 1
        profile.save()

        # JSON 응답 반환
        return JsonResponse({'success': True, 'message': 'CoffeeChat marked as COMPLETED.'})
    else:
        return JsonResponse({'success': False, 'message': '접근 권한이 없습니다.'})



def coffeechat_to_rejected(request, pk):
    coffeechat = get_object_or_404(CoffeeChat, pk=pk)

    if request.user == coffeechat.user or request.user == coffeechat.profile.user:
        coffeechat.status = 'REJECTED'
        coffeechat.save()  # 변경 사항 저장

        # JSON 응답 반환
        return JsonResponse({'success': True, 'message': 'CoffeeChat marked as REJECTED.'})
    else:
        return JsonResponse({'success': False, 'message': '접근 권한이 없습니다.'})



#메모 조회 및 수정 가능한 상태
@login_required
def memo(request, pk, re):

    saved_memo = get_object_or_404(Memo, pk=pk, user=request.user)

    # 작성자가 request.user와 다른 경우 에러 메시지 반환
    if saved_memo.user != request.user:
        return render(request, 'error/403.html', status=403)

    context = memo_context(saved_memo)

    #출력할 HTML 결정
    if re == 'ing':
        reHTML = 'mypage/mychatingdetail.html'
    else:
        reHTML = 'mypage/mychatenddetail.html'

    if request.method == "POST":
        # 폼 데이터에서 내용 가져오기
        content = request.POST.get("content", "").strip()


        # 메모 내용 저장: 공백이어도 좋다.
        saved_memo.content = content
        saved_memo.save()
        messages.success(request, "메모가 성공적으로 저장되었습니다.")

        #새로운 페이지 생성
        context = memo_context(saved_memo)
        return render(request, reHTML, context)

    return render(request, reHTML, context)


def memo_context(saved_memo):

    coffeechat = saved_memo.coffeeChatRequest  
    profile_user = coffeechat.profile.user

    # 현재 로그인한 사용자가 커피챗 신청자인지 확인
    is_requester = saved_memo.user == coffeechat.user

     # is_requester 여부에 따라 상대방 정보 설정
    if is_requester:
        other_user = coffeechat.profile.user  # 신청 받은 사람
    else:
        other_user = coffeechat.user  # 신청한 사람
    
    context = {
        "memo": {
            "id": saved_memo.id,
            "accepted_date": coffeechat.accepted_at,
            "profile_user": other_user.username,  # 상대방 이름
            "coffeechat": coffeechat.id,
            "memo_content": saved_memo.content,
            "is_requester": is_requester,
        }
    }
    return context

#리뷰 생성 메서드
def create_review(request, pk):

    coffeechat = get_object_or_404(CoffeeChat, pk=pk)

    if request.method == 'POST':
        user = request.user
        content = request.POST.get('content')
        profile = coffeechat.profile

        try:
            # 이미 Review가 존재하는 경우 예외 처리
            if Review.objects.filter(coffeechat_request=coffeechat).exists():
                return {'message': '이미 리뷰를 작성하셨습니다.'}

            review = Review.objects.create(
                coffeechat_request=coffeechat,
                user=user,
                content=content
            )
            return redirect('mypage:coffeechat_completed')
        except Exception as e:
            return {'message': '리뷰 생성에 실패하였습니다.'}

    context = {
        'profile_name': coffeechat.profile.user.username,
        'pk': pk
    }

    return render(request, "mypage/mychatreview.html", context)

def get_review(request, pk):

    coffeechat = get_object_or_404(CoffeeChat, pk=pk)
    profile = coffeechat.profile
    review = get_object_or_404(Review, coffeechat_request=coffeechat)

    context = {
        "review":
            {
                "id": review.id,
                "my_name": request.user.username,
                "profile_user": profile.user.username,
                "profile_user_id": profile.user.id,
                "review_content": review.content,
            }
    }
    return render(request, "mypage/mychatreview_get.html", context)

'''
    지금 사용 안하는 메서드
    스크랩 정보는 mypage 접근하면서 같이 전송
'''
@login_required
def scraped(request):
    # 현재 사용자와 관련된 모든 Scrap 객체 가져오기
    scraped_data = Scrap.objects.filter(user=request.user)

    # Scrap 객체에서 profile 필드를 리스트로 추출
    profiles = [scrap.profile for scrap in scraped_data]

    context = {
        'profiles': profiles,  # Profile 객체의 리스트
    }
    return render(request, 'mypage/scraps.html', context)
