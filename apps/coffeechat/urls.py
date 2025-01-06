from django.urls import path
from . import views

app_name = 'coffeechat'

urlpatterns = [
    path('main/', views.home, name='main'),
    path('create/', views.create, name='coffeechat_create'),
    path('detail/<int:pk>/', views.detail, name='coffeechat_detail'),
    path('update/<int:pk>/', views.update, name='coffeechat_update'),
    path('delete/<int:pk>/', views.delete, name='coffeechat_delete'),

    path('accept_request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject_request/<int:request_id>/', views.reject_request, name='reject_request'),
    path('review/<int:coffeechat_request_id>/create/', views.create_review, name='review_create'),

    path('howto/', views.howto, name='coffeechat_howto'),
    path('how_received/', views.how_received, name='coffeechat_how_received'),

    path('cohort/<int:cohort>/', views.cohort_profiles, name='cohort_profiles'),
    
    path('<int:pk>/bookmark/', views.bookmark_profile, name='coffeechat_bookmark'),
    
    path('coffeechat/<int:profile_id>/toggle_visibility/', views.toggle_visibility, name='toggle_visibility'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
