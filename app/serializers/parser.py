from rest_framework import serializers
from app.models.parser import Resume

class ResumeSerializer(serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    modified_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = ('id', 'parsing_status', 'no_of_retries', 'parsed_data_id', 'created_at', 'modified_at','storage_path','resume_category')
