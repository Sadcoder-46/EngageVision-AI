from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def ai_dashboard(request):
    """
    AI Dashboard - Redirects to analytics dashboard
    """
    return redirect('analytics:dashboard')


@login_required
def ai_camera(request):
    """
    AI Camera view - Redirects to video upload since webcam is not used
    """
    messages.info(request, "Please upload CCTV video footage for AI processing.")
    return redirect('engagement:upload_video')

