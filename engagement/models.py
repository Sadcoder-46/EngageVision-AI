from django.db import models
import os
from django.utils import timezone


def video_upload_path(instance, filename):
    """Generate upload path for video files"""
    ext = filename.split('.')[-1]
    filename = f"{instance.uploaded_at.strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('videos/', filename)


class VideoUpload(models.Model):
    """
    Model for storing uploaded CCTV video files
    """
    title = models.CharField(max_length=255, blank=True, default='CCTV Recording')
    video_file = models.FileField(upload_to=video_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processing_status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    duration_seconds = models.FloatField(null=True, blank=True)
    total_frames = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Video {self.id} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"


class EngagementRecord(models.Model):
    """
    AI-generated engagement record from video analysis
    Stores aggregated engagement metrics per time interval
    """
    BEHAVIOR_CHOICES = [
        ('Attentive', 'Attentive'),
        ('Sleepy', 'Sleepy'),
        ('Distracted', 'Distracted'),
        ('Neutral', 'Neutral'),
    ]
    
    video_upload = models.ForeignKey(
        VideoUpload, 
        on_delete=models.CASCADE, 
        related_name='engagement_records',
        null=True,
        blank=True
    )
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Detection counts
    total_students = models.IntegerField(default=0)
    attentive_count = models.IntegerField(default=0)
    sleepy_count = models.IntegerField(default=0)
    distracted_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)
    
    # Calculated metrics
    engagement_percentage = models.FloatField(default=0.0)
    
    # Frame information
    frame_number = models.IntegerField(null=True, blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Time taken to process this frame in seconds")
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Engagement {self.id} - {self.engagement_percentage:.1f}% at {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """Calculate engagement percentage automatically"""
        if self.total_students > 0:
            self.engagement_percentage = (self.attentive_count / self.total_students) * 100
        else:
            self.engagement_percentage = 0.0
        super().save(*args, **kwargs)

