
from django.urls import path
from . import views

app_name = 'ai_module'

urlpatterns = [
    path('', views.ai_dashboard, name='ai_dashboard'),
    path('camera/', views.ai_camera, name='ai_camera'),
]


