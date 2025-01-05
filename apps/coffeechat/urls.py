from django.urls import path
from . import views2

app_name = 'coffeechat'

urlpatterns = [
    path('main/', views2.home, name='main'), 
    path('create/', views2.create, name='coffeechat_create'),
    path('detail/<int:pk>/', views2.detail, name='coffeechat_detail'),
    path('update/<int:pk>/', views2.update, name='coffeechat_update'),
    path('delete/<int:pk>/', views2.delete, name='coffeechat_delete'),

    path('accept_request/<int:request_id>/', views2.accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', views2.reject_request, name='reject_request'),
    path('review/<int:coffeechat_request_id>/create/', views2.create_review, name='review_create'),

    path('howto/', views2.howto, name='coffeechat_howto'),
    path('how_received/', views2.how_received, name='coffeechat_how_received'),

    path('cohort/<int:cohort>/', views2.cohort_profiles, name='cohort_profiles'),
    
    path('<int:pk>/bookmark/', views2.bookmark_profile, name='coffeechat_bookmark'),
    
    path('coffeechat/<int:profile_id>/toggle_visibility/', views2.toggle_visibility, name='toggle_visibility'),
]
