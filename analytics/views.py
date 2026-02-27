from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
from engagement.models import VideoUpload, EngagementRecord


@login_required
def dashboard(request):
    """
    Main dashboard showing overview of AI-generated engagement data
    """
    # Get latest video and its records
    latest_video = VideoUpload.objects.filter(processed=True).first()
    
    # Get latest session data
    latest_records = EngagementRecord.objects.all().order_by('-timestamp')[:100]
    
    # Calculate aggregate statistics
    total_records = EngagementRecord.objects.count()
    
    # Get totals across all records
    totals = EngagementRecord.objects.aggregate(
        total_students=Sum('total_students'),
        total_attentive=Sum('attentive_count'),
        total_sleepy=Sum('sleepy_count'),
        total_distracted=Sum('distracted_count'),
        total_neutral=Sum('neutral_count'),
        avg_engagement=Avg('engagement_percentage'),
        max_engagement=Max('engagement_percentage'),
        min_engagement=Min('engagement_percentage'),
    )
    
    # Calculate current session stats (latest video)
    if latest_video:
        video_records = EngagementRecord.objects.filter(video_upload=latest_video)
        current_session = video_records.aggregate(
            avg_engagement=Avg('engagement_percentage'),
            max_students=Max('total_students'),
            total_detections=Sum('total_students'),
        )
    else:
        current_session = {
            'avg_engagement': 0,
            'max_students': 0,
            'total_detections': 0,
        }
    
    # Behavior distribution
    behavior_counts = {
        'Attentive': EngagementRecord.objects.aggregate(
            total=Sum('attentive_count')
        )['total'] or 0,
        'Sleepy': EngagementRecord.objects.aggregate(
            total=Sum('sleepy_count')
        )['total'] or 0,
        'Distracted': EngagementRecord.objects.aggregate(
            total=Sum('distracted_count')
        )['total'] or 0,
        'Neutral': EngagementRecord.objects.aggregate(
            total=Sum('neutral_count')
        )['total'] or 0,
    }
    
    # Recent records
    recent_records = EngagementRecord.objects.select_related(
        'video_upload'
    ).order_by('-timestamp')[:10]
    
    # Daily averages for last 7 days
    daily_data = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=i)
        day_records = EngagementRecord.objects.filter(timestamp__date=date)
        if day_records.exists():
            avg = day_records.aggregate(avg=Avg('engagement_percentage'))['avg']
            daily_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'label': date.strftime('%b %d'),
                'avg_engagement': round(avg, 2) if avg else 0,
                'record_count': day_records.count()
            })
    
    # Get videos for dropdown
    videos = VideoUpload.objects.all()[:5]
    
    context = {
        'total_records': total_records,
        'latest_video': latest_video,
        'current_session': current_session,
        'totals': totals,
        'behavior_counts': behavior_counts,
        'recent_records': recent_records,
        'daily_data': daily_data,
        'videos': videos,
    }
    
    return render(request, 'analytics/dashboard.html', context)


@login_required
def analytics(request):
    """
    Detailed analytics page with charts and filters
    """
    # Get filter parameters
    video_id = request.GET.get('video')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queryset
    records = EngagementRecord.objects.select_related('video_upload')
    
    # Apply filters
    if video_id:
        records = records.filter(video_upload_id=video_id)
    
    if date_from:
        records = records.filter(timestamp__date__gte=date_from)
    
    if date_to:
        records = records.filter(timestamp__date__lte=date_to)
    
    # Calculate statistics
    total_records = records.count()
    
    stats = records.aggregate(
        avg_engagement=Avg('engagement_percentage'),
        max_engagement=Max('engagement_percentage'),
        min_engagement=Min('engagement_percentage'),
        avg_students=Avg('total_students'),
        max_students=Max('total_students'),
    )
    
    # Behavior totals
    behavior_totals = records.aggregate(
        total_attentive=Sum('attentive_count'),
        total_sleepy=Sum('sleepy_count'),
        total_distracted=Sum('distracted_count'),
        total_neutral=Sum('neutral_count'),
    )
    
    total_behaviors = (
        (behavior_totals['total_attentive'] or 0) +
        (behavior_totals['total_sleepy'] or 0) +
        (behavior_totals['total_distracted'] or 0) +
        (behavior_totals['total_neutral'] or 0)
    )
    
    # Calculate percentages
    if total_behaviors > 0:
        behavior_percentages = {
            'Attentive': round((behavior_totals['total_attentive'] or 0) / total_behaviors * 100, 1),
            'Sleepy': round((behavior_totals['total_sleepy'] or 0) / total_behaviors * 100, 1),
            'Distracted': round((behavior_totals['total_distracted'] or 0) / total_behaviors * 100, 1),
            'Neutral': round((behavior_totals['total_neutral'] or 0) / total_behaviors * 100, 1),
        }
    else:
        behavior_percentages = {
            'Attentive': 0,
            'Sleepy': 0,
            'Distracted': 0,
            'Neutral': 0,
        }
    
    # Get data for charts
    # Time series data
    time_series = []
    for record in records.order_by('timestamp')[:100]:
        time_series.append({
            'timestamp': record.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'engagement': record.engagement_percentage,
            'total_students': record.total_students,
            'attentive': record.attentive_count,
            'sleepy': record.sleepy_count,
            'distracted': record.distracted_count,
            'neutral': record.neutral_count,
        })
    
    # Daily averages
    daily_averages = records.extra(
        select={'day': 'date(timestamp)'}
    ).values('day').annotate(
        avg_engagement=Avg('engagement_percentage'),
        avg_students=Avg('total_students'),
        record_count=Count('id')
    ).order_by('-day')[:30]
    
    # Videos for filter
    videos = VideoUpload.objects.all()
    
    context = {
        'total_records': total_records,
        'stats': stats,
        'behavior_totals': behavior_totals,
        'behavior_percentages': behavior_percentages,
        'time_series': time_series,
        'daily_averages': list(daily_averages),
        'videos': videos,
        'selected_video': video_id,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'analytics/analytics.html', context)


# Import Sum if not already imported
from django.db.models import Sum

