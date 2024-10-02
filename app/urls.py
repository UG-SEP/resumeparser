from django.urls import path
from app.Views import resume_upload_view

urlpatterns = [
    path('upload/',resume_upload_view, name='resume-upload'),
]
