from django.contrib import admin
from .models import VideoUpload, EngagementRecord


@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'uploaded_at', 'processed', 'processing_status', 'duration_seconds']
    list_filter = ['processed', 'processing_status', 'uploaded_at']
    search_fields = ['title']
    readonly_fields = ['uploaded_at', 'processed', 'processing_status', 'total_frames']
    ordering = ['-uploaded_at']


@admin.register(EngagementRecord)
class EngagementRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'video_upload', 'timestamp', 'total_students',
        'attentive_count', 'sleepy_count', 'distracted_count',
        'neutral_count', 'engagement_percentage'
    ]
    list_filter = ['timestamp', 'video_upload']
    search_fields = ['video_upload__title']
    readonly_fields = [
        'video_upload', 'timestamp', 'total_students',
        'attentive_count', 'sleepy_count', 'distracted_count',
        'neutral_count', 'engagement_percentage', 'frame_number'
    ]
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        # Disable manual addition - records are AI-generated only
        return False
    
    def has_change_permission(self, request, obj=None):
        # Disable manual editing
        return False

