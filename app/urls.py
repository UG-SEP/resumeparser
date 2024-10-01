from django.urls import path
from app.Views.parser import ResumeUploadView

urlpatterns = [
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
]
