from django.db import models
import uuid

class Resume(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    CATEGORY_CHOICES = [
        ('frontend', 'Frontend'),
        ('backend', 'Backend'),
        ('fullstack', 'Fullstack'),
        ('android', 'Android'),
        ('data_scientist', 'Data Scientist'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='resumes/')
    storage_path = models.CharField(max_length=255, blank=True, null=True)
    parsing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    no_of_retries = models.IntegerField(default=0)
    parsed_data_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    resume_category = models.CharField(max_length=20, choices=CATEGORY_CHOICES,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume {self.id} - {self.parsing_status}"
