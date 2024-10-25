# Generated by Django 4.2.16 on 2024-10-25 14:58

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to='resumes/')),
                ('storage_path', models.CharField(blank=True, max_length=255, null=True)),
                ('parsing_status', models.CharField(choices=[('in_progress', 'In Progress'), ('completed', 'Completed'), ('failed', 'Failed')], default='in_progress', max_length=20)),
                ('no_of_retries', models.IntegerField(default=0)),
                ('parsed_data_id', models.CharField(editable=False, max_length=200)),
                ('resume_category', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
