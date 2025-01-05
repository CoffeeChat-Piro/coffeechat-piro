from django.urls import path
from . import views

app_name = 'mypage'

urlpatterns = [
    # path('', views.ProfileView.as_view(), name='profile'),
    # path('edit/', views.ProfileEditView.as_view(), name='profile_edit'),


    path('', views.mypageView.as_view(), name='profile'),
    path('edit/', views.mypageEditView.as_view(), name='profile_edit'),
    ####
    path('password', views.password_change, name='password'),                                            #비밀번호 수정                                             #스크랩한 프로필
    path('ajax/coffeechat/received', views.coffeechat_received, name='coffeechat_received'),     #커피챗 현환-받은
    path('ajax/coffeechat/requested', views.coffeechat_requested, name='coffeechat_requested'),  #커피챗 현황-한
    path('ajax/coffeechat/in-progress', views.coffeechat_in_progress, name='coffeechat_in_progress'),     #커피챗 현황-진행중
    path('ajax/coffeechat/completed', views.coffeechat_completed, name='coffeechat_completed'),           #커피챗 현황-완료
    path('memo/<int:pk>/<str:re>', views.memo, name='coffeechat_memo'),                                           #메모 조회 수정
    # path('memo/<int:pk>', views.scraped, name='scraped_profiled'),

    #review 관련 메서드
    path('review/<int:pk>/create', views.create_review, name='create_review'),

    #complete로 전환
    path('coffeechat/<int:pk>/complete', views.coffeechat_to_complete, name='coffeechat_to_complete'),
    path('coffeechat/<int:pk>/rejected', views.coffeechat_to_rejected, name='coffeechat_to_rejected'),

    ####4

    path('ajax/activities/', views.ActivitiesAjaxView.as_view, name='ajax_activities'),
    path('ajax/profile-modal/', views.profile_modal_view, name='profile_modal'),
    path('profile/<int:user_id>/', views.profile_read, name='profile_read'),
    path('bookmark/<int:pk>/', views.coffeechat_bookmark_profile, name='coffeechat_bookmark_profile'),
]