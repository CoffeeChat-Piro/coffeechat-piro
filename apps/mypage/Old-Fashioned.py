# class ActivitiesAjaxView(LoginRequiredMixin, TemplateView):
#     def get(self, request, *args, **kwargs):
#         filter_type = request.GET.get('filter', 'my_posts')
#         category = request.GET.get('category', 'all')
#         user_id = request.GET.get('user_id', None)
#
#         # 특정 사용자 글 필터링하기 위해 user_id 사용
#         if user_id:
#             target_user = get_object_or_404(User, id=user_id)
#         else:
#             target_user = request.user
#
#         # 커피챗 필터링
#         if filter_type == 'coffeechat':
#             if category == 'requests_sent':
#                 requests_sent = CoffeeChat.objects.filter(user=target_user, status='WAITING')
#                 data = [{
#                     'sender': request.user.username,
#                     'receiver': request.profile.user.username,
#                     'job': request.profile.job,
#                     'created_at': request.created_at.isoformat(),
#                     'status': request.get_status_display(),
#                     'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[request.profile.id]),
#                     'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.profile.user.id]),
#                 } for request in requests_sent]
#                 print("Debug Data for requests_sent:", data)
#                 return JsonResponse({'requests_sent': data})
#
#             elif category == 'requests_received':
#                 requests_received = CoffeeChat.objects.filter(coffeechat__receiver=target_user, status='WAITING')
#                 data = []
#                 debug_data = []
#
#                 for request in requests_received:
#                     sender_username = request.user.username
#                     sender_id = request.user.id
#                     receiver_username = request.profile.user.username if request.profile.user else 'Unknown'
#                     job = request.profile.job
#                     detail_url = reverse_lazy('coffeechat:coffeechat_detail', args=[request.profile.id])
#                     cohort = request.user.cohort  # 신청한 사람의 기수
#
#                     # 디버깅 정보 리스트
#                     debug_data.append({
#                         'request_id': request.id,
#                         'coffeechat_id': request.profile.id,
#                         'sender_username': sender_username,
#                         'receiver_username': receiver_username,
#                         'job': job,
#                         'cohort': cohort,  # 추가된 부분
#                         'detail_url': detail_url,
#                         'status': request.status,
#                         'receiver_id': request.profile.user.id if request.profile.user else 'None',
#                         'sender_id': request.user.id,
#                         'letter_to_senior': request.letterToSenior,  # 추가된 부분
#
#                     })
#
#
#                     data.append({
#                         'sender': sender_username,
#                         'sender_id': sender_id,
#                         'receiver': receiver_username,
#                         'job': job,
#                         'cohort': cohort,  # 추가된 부분
#                         'created_at': request.created_at.isoformat(),
#                         'status': request.get_status_display(),
#                         'detail_url': detail_url,
#                         'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.profile.user.id if request.profile.user else '']),
#                         'accept_url': reverse_lazy('coffeechat:accept_request', args=[request.id]),
#                         'reject_url': reverse_lazy('coffeechat:reject_request', args=[request.id]),
#                         'letter_to_senior': request.letterToSenior,  # 추가된 부분
#                     })
#
#                 # 디버깅 정보를 출력
#                 print("Debug Data for requests_received:", debug_data)
#
#                 return JsonResponse({'requests_received': data})
#
#             elif category == 'bookmarked':
#                 bookmarked_coffeechats = Profile.objects.filter(bookmarks=target_user)
#                 data = [{
#                     'receiver': coffeechat.user.username,
#                     'job': coffeechat.job,
#                     'created_at': coffeechat.created_at.isoformat(),
#                     'content': coffeechat.content,
#                     'hashtags': [hashtag.name for hashtag in coffeechat.hashtags.all()],
#                     'bookmarked': True,
#                     'coffeechat_bookmark_profile': reverse_lazy('mypage:coffeechat_bookmark_profile', args=[coffeechat.id]),
#                     'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[coffeechat.id]),
#                     'profile_read_url': reverse_lazy('mypage:profile_read', args=[coffeechat.user.id if coffeechat.user else '']),
#                 } for coffeechat in bookmarked_coffeechats]
#                 return JsonResponse({'bookmarked_coffeechats': data})
#
#             elif category == 'history':
#                 accepted_requests = CoffeeChat.objects.filter(user=target_user, status='ACCEPTED')
#                 data = [{
#                     'sender': request.user.username,
#                     'receiver': request.profile.user.username,
#                     'job': request.profile.job,
#                     'created_at': request.created_at.isoformat(),
#                     'status': request.get_status_display(),
#                     'hashtags': [hashtag.name for hashtag in request.profile.hashtags.all()],
#                     'review': {
#                         'rating': request.review.rating if hasattr(request, 'review') else None,
#                         'content': request.review.content if hasattr(request, 'review') else None,
#                         'created_at': request.review.created_at.isoformat() if hasattr(request, 'review') else None,
#                     } if hasattr(request, 'review') else None,
#                     'detail_url': reverse_lazy('coffeechat:coffeechat_detail', args=[request.profile.id]),
#                     'profile_read_url': reverse_lazy('mypage:profile_read', args=[request.profile.user.id]),
#                     'review_exists': True if hasattr(request, 'review') else False,
#                 } for request in accepted_requests]
#                 return JsonResponse({'accepted_requests': data})
#
#         # 내 정보 보기
#         elif filter_type == 'profile_info':
#             user = target_user
#             data = {
#                 'username': user.username,
#                 'email': user.email,
#                 'profile_image': user.profile_image.url if user.profile_image else None,
#                 'cohort': user.cohort,
#                 'intro': user.intro,
#             }
#             return JsonResponse(data)
#
