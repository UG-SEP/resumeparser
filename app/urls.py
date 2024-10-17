from django.urls import path
from app.Views import resume_upload_view,retrieve_data_view

urlpatterns = [
    path('upload/',resume_upload_view, name='resume-upload'),
    path('retrieve-data/',retrieve_data_view,name='retrieve-data')
]
