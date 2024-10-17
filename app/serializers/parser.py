from rest_framework import serializers
from app.models import Resume
from django.core.exceptions import ValidationError
import json
import re

class ResumeSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    modified_at = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Resume
        fields = '__all__'
        read_only_fields = (
            'id', 'parsing_status', 'no_of_retries', 
            'parsed_data_id', 'created_at', 'modified_at',
            'storage_path', 'resume_category'
        )

    def create(self, validated_data):
        return Resume.objects.create(**validated_data)

    def create_bulk(self, files):
        resume_objects = [Resume(file=file) for file in files]
        return Resume.bulk_create_resume(resume_objects)

class ProficiencySerializer(serializers.Serializer):
    proficient = serializers.ListField(child=serializers.CharField(), max_length=3, required=False)
    average = serializers.ListField(child=serializers.CharField(), required=False)

class SkillSerializer(serializers.Serializer):
    languages = ProficiencySerializer(required=False)
    frameworks = ProficiencySerializer(required=False)
    technologies = ProficiencySerializer(required=False)
    total_skill_experience = serializers.DictField(required=False)
    llm_experience = serializers.BooleanField(required=False)
    gen_ai_experience = serializers.BooleanField(required=False)


class CompanyInformationSerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    last_position_held = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    joining_month_and_year = serializers.CharField(required=False)
    leaving_month_and_year = serializers.CharField(required=False)
    total_duration_in_years = serializers.IntegerField(required=False)
    company_size_range = serializers.CharField(required=False)
    total_capital_raised = serializers.CharField(required=False)
    company_type = serializers.CharField(required=False)
    is_faang = serializers.BooleanField(required=False)
    has_the_company_raised_capital_in_the_last_5_years = serializers.CharField(required=False)
    is_startup = serializers.BooleanField(required=False)

class ExperienceSerializer(serializers.Serializer):
    company_information = CompanyInformationSerializer()
    positions_held_within_the_company = serializers.ListField(child=serializers.DictField())

class EducationSerializer(serializers.Serializer):
    school_name = serializers.CharField(required=False)
    degree_name = serializers.CharField(required=False)
    city = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    year_of_start = serializers.IntegerField(required=False)
    year_of_graduation = serializers.IntegerField(required=False)
    duration_in_years = serializers.IntegerField(required=False)
    mode = serializers.CharField(required=False)
    degree_level = serializers.CharField(required=False)
    is_cs_degree = serializers.BooleanField(required=False)
    is_ml_degree = serializers.BooleanField(required=False)
    institute_type = serializers.CharField(required=False)

class ParsedResumeSerializer(serializers.Serializer):
    personal_information = serializers.DictField()
    resume_type = serializers.CharField()
    title = serializers.CharField(required=False)
    skills = SkillSerializer()
    education = EducationSerializer(many=True)
    experience = ExperienceSerializer(many=True, required=False)
    projects_outside_of_work = serializers.ListField(child=serializers.DictField(), required=False)
    additional_experience_summary = serializers.DictField()
    achievements_awards = serializers.DictField()
    overall_summary_of_candidate = serializers.CharField()

    def try_fix_json_string(self, json_string):
        try:
            json_string = re.sub(r',\s*([\]}])', r'\1', json_string) 
            json_string = json_string.replace("'", '"')  
            json_string = re.sub(r'([{,]\s*)(\w+)\s*:', r'\1"\2":', json_string)
            
            if not json_string.startswith(('{', '[')):
                json_string = '{' + json_string + '}'
            
            return json.loads(json_string)
        
        except json.JSONDecodeError as e:
            logger.info(f"Unable to fix json: {json_string}")
            return None

    def fix_json(self, data):
     
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self.fix_json(value)  
            elif isinstance(value, list):
                data[key] = [self.fix_json(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str):
                if value.isdigit():
                    data[key] = int(value)
            
            elif value is None or value == "":
                data[key] = "null"
        return data

    def validate(self, data):
        if isinstance(data, str):
            data = self.try_fix_json_string(data)
            if data is None:
                raise serializers.ValidationError("Invalid JSON format.")

        fixed_data = self.fix_json(data)

        return super().validate(fixed_data)

def to_internal_value(self, data):
    try:
        fixed_data = self.fix_json(data)
        return super().to_internal_value(fixed_data)
    except ValueError as e:
        logger.error(f"ValueError during data processing: {e}",exc_info=True)
        raise serializers.ValidationError("Invalid data structure provided.")
    except Exception as e:
        logger.error(f"Error during data fixing: {e}",exc_info=True)
        raise serializers.ValidationError("Unexpected error occurred while processing data.")
