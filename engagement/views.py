from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import VideoUpload, EngagementRecord
from .forms import VideoUploadForm
from .ai_engine import process_video, simulate_processing
import threading
import logging

logger = logging.getLogger(__name__)


def process_video_async(video_upload_id, video_path):
    """
    Background task to process video asynchronously
    """
    from engagement.models import VideoUpload
    
    try:
        # Update status to processing
        video_upload = VideoUpload.objects.get(id=video_upload_id)
        video_upload.processing_status = 'processing'
        video_upload.save()
        
        # Try to process with OpenCV
        try:
            import cv2
            result = process_video(video_path, video_upload_id, save_interval=30)
        except ImportError:
            # Fall back to simulation if OpenCV not available
            logger.warning("OpenCV not available, using simulated processing")
            result = simulate_processing(video_upload_id)
        
        # Update video upload status
        video_upload = VideoUpload.objects.get(id=video_upload_id)
        
        if result.get('success'):
            video_upload.processed = True
            video_upload.processing_status = 'completed'
            if 'total_frames' in result:
                video_upload.total_frames = result['total_frames']
            if 'processing_time' in result:
                video_upload.duration_seconds = result['processing_time']
        else:
            video_upload.processing_status = 'failed'
        
        video_upload.save()
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        try:
            video_upload = VideoUpload.objects.get(id=video_upload_id)
            video_upload.processing_status = 'failed'
            video_upload.save()
        except:
            pass


@login_required
def engagement_list(request):
    """
    List all engagement records with pagination and filters
    """
    records = EngagementRecord.objects.all().select_related('video_upload')
    
    # Filter by video
    video_id = request.GET.get('video')
    if video_id:
        records = records.filter(video_upload_id=video_id)
    
    # Filter by date
    date_filter = request.GET.get('date')
    if date_filter:
        records = records.filter(timestamp__date=date_filter)
    
    # Filter by engagement level
    engagement_filter = request.GET.get('engagement')
    if engagement_filter:
        if engagement_filter == 'high':
            records = records.filter(engagement_percentage__gte=70)
        elif engagement_filter == 'medium':
            records = records.filter(engagement_percentage__gte=40, engagement_percentage__lt=70)
        elif engagement_filter == 'low':
            records = records.filter(engagement_percentage__lt=40)
    
    paginator = Paginator(records, 20)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)
    
    # Get videos for filter dropdown
    videos = VideoUpload.objects.all()
    
    return render(request, 'engagement/engagement_list.html', {
        'records': records,
        'videos': videos
    })


@login_required
def engagement_detail(request, pk):
    """
    View detailed engagement record
    """
    record = get_object_or_404(
        EngagementRecord.objects.select_related('video_upload'),
        pk=pk
    )
    return render(request, 'engagement/engagement_detail.html', {'record': record})


@login_required
def engagement_delete(request, pk):
    """
    Delete an engagement record
    """
    record = get_object_or_404(EngagementRecord, pk=pk)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Engagement record deleted successfully!")
        return redirect('engagement:engagement_list')
    return render(request, 'engagement/engagement_confirm_delete.html', {'record': record})


@login_required
def upload_video(request):
    """
    Handle video upload and trigger AI processing
    """
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_upload = form.save()
            
            # Start async processing
            video_path = video_upload.video_file.path
            thread = threading.Thread(
                target=process_video_async,
                args=(video_upload.id, video_path)
            )
            thread.start()
            
            messages.success(
                request, 
                "Video uploaded successfully! Processing has started in the background."
            )
            return redirect('engagement:video_list')
    else:
        form = VideoUploadForm()
    
    return render(request, 'engagement/upload_video.html', {'form': form})


@login_required
def video_list(request):
    """
    List all uploaded videos with their processing status
    """
    videos = VideoUpload.objects.all()
    paginator = Paginator(videos, 10)
    page_number = request.GET.get('page')
    videos = paginator.get_page(page_number)
    
    return render(request, 'engagement/video_list.html', {'videos': videos})


@login_required
def video_detail(request, pk):
    """
    View details of a specific video upload
    """
    video = get_object_or_404(VideoUpload, pk=pk)
    records = EngagementRecord.objects.filter(video_upload=video).order_by('timestamp')
    
    return render(request, 'engagement/video_detail.html', {
        'video': video,
        'records': records
    })


@login_required
@require_http_methods(["DELETE"])
def video_delete(request, pk):
    """
    Delete a video upload and its associated records
    """
    video = get_object_or_404(VideoUpload, pk=pk)
    video.video_file.delete()
    video.delete()
    return JsonResponse({'success': True})


@login_required
def get_processing_status(request, video_id):
    """
    AJAX endpoint to check video processing status
    """
    video = get_object_or_404(VideoUpload, pk=video_id)
    
    return JsonResponse({
        'status': video.processing_status,
        'processed': video.processed,
        'total_frames': video.total_frames,
        'duration_seconds': video.duration_seconds
    })


# Legacy views - kept for backward compatibility but deprecated
# These now redirect to video upload since manual entry is removed

@login_required
def engagement_create(request):
    """Redirect to video upload since manual entry is no longer supported"""
    messages.info(request, "Engagement records are now automatically generated from video uploads.")
    return redirect('engagement:upload_video')


@login_required
def engagement_update(request, pk):
    """Redirect to list since manual editing is no longer supported"""
    messages.info(request, "Engagement records are automatically generated and cannot be manually edited.")
    return redirect('engagement:engagement_list')

