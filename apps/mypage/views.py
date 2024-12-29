# Django 내장 모듈
from django.views.generic import TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# 프로젝트 내 모듈
from apps.accounts.models import CustomUser
from apps.accounts.forms import CustomUserChangeForm
# from apps.review.models import Review, Comment as ReviewComment
# from apps.corboard.models import Corboard, Comment as CorboardComment
# from apps.trend.models import Trend, Comment as TrendComment
from apps.coffeechat.models import CoffeeChat, CoffeeChatRequest
from apps.coffeechat.forms import WayToContect

# 프로필 보기 뷰
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'mypage/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        return context

# 프로필 수정 뷰
class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = CustomUser
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
            target_user = get_object_or_404(CustomUser, id=user_id)
        else:
            target_user = request.user

        # 내가 쓴 글 필터링
        # if filter_type == 'my_posts':
        #     if category == 'review':
        #         posts = Review.objects.filter(writer=target_user)
        #     elif category == 'trend':
        #         posts = Trend.objects.filter(writer=target_user)
        #     elif category == 'corboard':
        #         posts = Corboard.objects.filter(writer=target_user)
        #     else:
        #         posts = list(Trend.objects.filter(writer=target_user)) + \
        #                 list(Review.objects.filter(writer=target_user)) + \
        #                 list(Corboard.objects.filter(writer=target_user))

        # 내가 북마크한 글 필터링
        # elif filter_type == 'bookmarked':
        #     if category == 'review':
        #         posts = Review.objects.filter(bookmarks=target_user)
        #     elif category == 'trend':
        #         posts = Trend.objects.filter(bookmarks=target_user)
        #     elif category == 'corboard':
        #         posts = Corboard.objects.filter(bookmarks=target_user)
        #     else:
        #         posts = list(Trend.objects.filter(bookmarks=target_user)) + \
        #                 list(Review.objects.filter(bookmarks=target_user)) + \
        #                 list(Corboard.objects.filter(bookmarks=target_user))

        # # 내가 좋아요한 글 필터링
        # elif filter_type == 'liked':
        #     if category == 'review':
        #         posts = Review.objects.filter(likes=target_user)
        #     elif category == 'trend':
        #         posts = Trend.objects.filter(likes=target_user)
        #     elif category == 'corboard':
        #         posts = Corboard.objects.filter(likes=target_user)
        #     else:
        #         posts = list(Trend.objects.filter(likes=target_user)) + \
        #                 list(Review.objects.filter(likes=target_user)) + \
        #                 list(Corboard.objects.filter(likes=target_user))

        # 내가 댓글을 단 글 필터링
        # elif filter_type == 'commented':
        #     if category == 'review':
        #         post_ids = ReviewComment.objects.filter(writer=target_user).values_list('review_id', flat=True)
        #         posts = Review.objects.filter(id__in=post_ids)
        #     elif category == 'trend':
        #         post_ids = TrendComment.objects.filter(writer=target_user).values_list('trend_id', flat=True)
        #         posts = Trend.objects.filter(id__in=post_ids)
        #     elif category == 'corboard':
        #         post_ids = CorboardComment.objects.filter(writer=target_user).values_list('corboard_id', flat=True)
        #         posts = Corboard.objects.filter(id__in=post_ids)
        #     else:
        #         trend_ids = TrendComment.objects.filter(writer=target_user).values_list('trend_id', flat=True)
        #         review_ids = ReviewComment.objects.filter(writer=target_user).values_list('review_id', flat=True)
        #         corboard_ids = CorboardComment.objects.filter(writer=target_user).values_list('corboard_id', flat=True)
        #         posts = list(Trend.objects.filter(id__in=trend_ids)) + \
        #                 list(Review.objects.filter(id__in=review_ids)) + \
        #                 list(Corboard.objects.filter(id__in=corboard_ids))

        # 커피챗 필터링
        if filter_type == 'coffeechat':
            if category == 'requests_sent':
                requests_sent = CoffeeChatRequest.objects.filter(user=target_user, status='WAITING')
                data = [{
                    'sender': request.user.username,
                    'receiver': request.coffeechat.receiver.username,
                    'job': request.coffeechat.job,
                    'created_at': request.created_at.isoformat(),
                    'status': request.get_status_display(),
                    'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[request.coffeechat.id]),
                    'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.coffeechat.receiver.id]),
                } for request in requests_sent]
                print("Debug Data for requests_sent:", data)
                return JsonResponse({'requests_sent': data})

            elif category == 'requests_received':
                requests_received = CoffeeChatRequest.objects.filter(coffeechat__receiver=target_user, status='WAITING')
                data = []
                debug_data = []

                for request in requests_received:
                    sender_username = request.user.username
                    sender_id = request.user.id
                    receiver_username = request.coffeechat.receiver.username if request.coffeechat.receiver else 'Unknown'
                    job = request.coffeechat.job
                    detail_url = reverse_lazy('coffeechat:coffeechat_detail', args=[request.coffeechat.id])
                    cohort = request.user.cohort  # 신청한 사람의 기수

                    # 디버깅 정보 리스트
                    debug_data.append({
                        'request_id': request.id,
                        'coffeechat_id': request.coffeechat.id,
                        'sender_username': sender_username,
                        'receiver_username': receiver_username,
                        'job': job,
                        'cohort': cohort,  # 추가된 부분
                        'detail_url': detail_url,
                        'status': request.status,
                        'receiver_id': request.coffeechat.receiver.id if request.coffeechat.receiver else 'None',
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
                        'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.coffeechat.receiver.id if request.coffeechat.receiver else '']),
                        'accept_url': reverse_lazy('coffeechat:accept_request', args=[request.id]),
                        'reject_url': reverse_lazy('coffeechat:reject_request', args=[request.id]),
                        'letter_to_senior': request.letterToSenior,  # 추가된 부분
                    })

                # 디버깅 정보를 출력
                print("Debug Data for requests_received:", debug_data)

                return JsonResponse({'requests_received': data})

            elif category == 'bookmarked':
                bookmarked_coffeechats = CoffeeChat.objects.filter(bookmarks=target_user)
                data = [{
                    'receiver': coffeechat.receiver.username,
                    'job': coffeechat.job,
                    'created_at': coffeechat.created_at.isoformat(),
                    'content': coffeechat.content,
                    'hashtags': [hashtag.name for hashtag in coffeechat.hashtags.all()],
                    'bookmarked': True,
                    'coffeechat_bookmark_profile': reverse_lazy('mypage:coffeechat_bookmark_profile', args=[coffeechat.id]),
                    'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[coffeechat.id]),
                    'profile_read_url': reverse_lazy('mypage:profile_read', args=[coffeechat.receiver.id if coffeechat.receiver else '']),
                } for coffeechat in bookmarked_coffeechats]
                return JsonResponse({'bookmarked_coffeechats': data})
            
            elif category == 'history':
                accepted_requests = CoffeeChatRequest.objects.filter(user=target_user, status='ACCEPTED')
                data = [{
                    'sender': request.user.username,
                    'receiver': request.coffeechat.receiver.username,
                    'job': request.coffeechat.job,
                    'created_at': request.created_at.isoformat(),
                    'status': request.get_status_display(),
                    'hashtags': [hashtag.name for hashtag in request.coffeechat.hashtags.all()],
                    'review': {
                        'rating': request.review.rating if hasattr(request, 'review') else None,
                        'content': request.review.content if hasattr(request, 'review') else None,
                        'created_at': request.review.created_at.isoformat() if hasattr(request, 'review') else None,
                    } if hasattr(request, 'review') else None,
                    'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[request.coffeechat.id]),
                    'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.coffeechat.receiver.id]),
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

        # else:
        #     posts = list(Trend.objects.filter(writer=target_user)) + \
        #             list(Review.objects.filter(writer=target_user)) + \
        #             list(Corboard.objects.filter(writer=target_user))

        # posts_data = [{
        #     'id': post.id,
        #     'type': post.__class__.__name__.lower(),
        #     'title': post.title, 
        #     'content': post.content[:100],
        #     'writer': post.writer.username,
        #     'writer_id': post.writer.id,
        #     'date': post.date.isoformat(),
        #     'url': post.get_absolute_url(),
        #     'category': getattr(post, 'category', '일반')
        # } for post in posts]

        # return JsonResponse({'posts': posts_data})

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

# @csrf_exempt
# def toggle_bookmark(request, post_type, post_id):
#     if request.method == 'POST':
#         try:
#             if post_type == 'review':
#                 post = Review.objects.get(id=post_id)
#             elif post_type == 'trend':
#                 post = Trend.objects.get(id=post_id)
#             elif post_type == 'corboard':
#                 post = Corboard.objects.get(id=post_id)
#             else:
#                 return JsonResponse({'error': 'Invalid post type'}, status=400)

#             if request.user in post.bookmarks.all():
#                 post.bookmarks.remove(request.user)
#                 return JsonResponse({'bookmarked': False})
#             else:
#                 post.bookmarks.add(request.user)
#                 return JsonResponse({'bookmarked': True})

#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def coffeechat_bookmark_profile(request, pk):
    profile = get_object_or_404(CoffeeChat, pk=pk)
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
    profile_user = get_object_or_404(CustomUser, id=user_id)

    image_files = ['back.png', 'back1.png', 'back2.png']
    random_image = random.choice(image_files)

    context = {
        'profile_user': profile_user,
        'random_image': random_image,
    }

    # 서버 로그에 출력
    print(f"Random Image URL: /static/images/{random_image}")

    return render(request, 'mypage/profile_modal.html', context)