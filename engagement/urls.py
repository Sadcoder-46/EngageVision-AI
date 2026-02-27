from django.urls import path
from . import views

app_name = 'engagement'

urlpatterns = [
    # Video upload URLs
    path('videos/', views.video_list, name='video_list'),
    path('videos/upload/', views.upload_video, name='upload_video'),
    path('videos/<int:pk>/', views.video_detail, name='video_detail'),
    path('videos/<int:pk>/delete/', views.video_delete, name='video_delete'),
    path('videos/<int:video_id>/status/', views.get_processing_status, name='video_status'),
    
    # Engagement record URLs
    path('', views.engagement_list, name='engagement_list'),
    path('records/<int:pk>/', views.engagement_detail, name='engagement_detail'),
    path('records/<int:pk>/delete/', views.engagement_delete, name='engagement_delete'),
    
    # Legacy URLs - redirected to new functionality
    path('add/', views.engagement_create, name='engagement_create'),
    path('<int:pk>/edit/', views.engagement_update, name='engagement_update'),
]

