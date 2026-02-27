from django.db import models

# Create your models here.from django.db import models
from django.contrib.auth.models import User

class EngagementRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    attention_score = models.FloatField()
    emotion = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.attention_score}"