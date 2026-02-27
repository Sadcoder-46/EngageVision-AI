from django import forms
from .models import VideoUpload, EngagementRecord


class VideoUploadForm(forms.ModelForm):
    """
    Form for uploading CCTV video files
    """
    class Meta:
        model = VideoUpload
        fields = ['title', 'video_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter video title (optional)'
            }),
            'video_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*'
            })
        }
    
    def clean_video_file(self):
        video_file = self.cleaned_data.get('video_file')
        if video_file:
            # Validate file extension
            allowed_extensions = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv']
            ext = video_file.name.split('.')[-1].lower()
            
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'Unsupported file format. Allowed formats: {", ".join(allowed_extensions)}'
                )
            
            # Validate file size (max 500MB)
            max_size = 500 * 1024 * 1024  # 500MB
            if video_file.size > max_size:
                raise forms.ValidationError(
                    f'Video file is too large. Maximum size is 500MB.'
                )
        
        return video_file


class EngagementRecordForm(forms.ModelForm):
    """
    Form for viewing engagement records (read-only)
    Note: Manual entry has been removed - records are now AI-generated
    """
    class Meta:
        model = EngagementRecord
        fields = [
            'video_upload', 'timestamp', 'total_students',
            'attentive_count', 'sleepy_count', 'distracted_count',
            'neutral_count', 'engagement_percentage'
        ]
        widgets = {
            'video_upload': forms.Select(attrs={'class': 'form-control'}),
            'timestamp': forms.DateTimeInput(attrs={'class': 'form-control'}),
            'total_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'attentive_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'sleepy_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'distracted_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'neutral_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'engagement_percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

