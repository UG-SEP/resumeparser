from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from app.tasks import process_resume_task
from app.serializers import ResumeSerializer, ResumeFilterSerializer
from app.models import Resume
from app.controllers import ResumeController
from resumeparser.settings import logger
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser


def get_serializer_parameters(serializer):
    parameters = []
    for field_name, field in serializer.get_fields().items():
        if field.read_only:
            continue
        param_type = openapi.TYPE_STRING
        
        
        if isinstance(field, serializers.BooleanField):
            param_type = openapi.TYPE_BOOLEAN
        elif isinstance(field, serializers.IntegerField):
            param_type = openapi.TYPE_INTEGER
        elif isinstance(field, serializers.FloatField):
            param_type = openapi.TYPE_NUMBER
        elif isinstance(field, serializers.FileField):
            param_type = openapi.TYPE_FILE  

        parameters.append(openapi.Parameter(
            field_name,
            openapi.IN_FORM,  
            description=field.help_text or '', 
            type=param_type,
            required=field.required
        ))
        
    return parameters


@swagger_auto_schema(
    method='post',
    manual_parameters=get_serializer_parameters(ResumeSerializer()), 
    responses={
        201: openapi.Response(
            description='Successful response',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="3 resumes uploaded and processing started."),
                }
            )
        ),
        400: openapi.Response(
            description='Bad request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'error': openapi.Schema(type=openapi.TYPE_STRING, example="No files uploaded.")
                }
            )
        )
    }
)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def resume_upload_view(request):
    
    resume_files = request.FILES.getlist('file')
        
    if not resume_files:
        return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
    # TODO: Extract the validated_data extract the instance_info and convert it into dict / json and then bulk save 
    # and pass to the process_resume_task
    serializer = ResumeSerializer()
    created_resumes = serializer.create_bulk(resume_files) 
    # resume_ids = [str(resume.id) for resume in created_resumes] 
    #  resumes = Resume.get_all(resume_id)
    # resume_ids = [resume.id for resume in created_resumes]
    for resume in created_resumes:
        print(resume)
        print(type(resume.id))
        process_resume_task.delay(resume.id)

    logger.info(f"{len(resume_files)} Resume has been passed to the celery task for background processing: ")
    return Response(
        {"message": f"{len(resume_files)} resumes uploaded and processing started."},
        status=status.HTTP_201_CREATED
    )
        


validation_error_response = openapi.Response(
    description="Validation Error",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'errors': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                additional_properties=openapi.Schema(type=openapi.TYPE_STRING),
                description="Detailed error messages for each invalid field"
            )
        },
        required=['errors']
    )
)

server_error_response = openapi.Response(
    description="Server Error",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'error': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Error message describing what went wrong"
            ),
            'details': openapi.Schema(
                type=openapi.TYPE_STRING,
                description="Optional additional details for debugging purposes"
            )
        },
        required=['error']
    )
)

success_response = openapi.Response(
    description="Successful Response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'data': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                description="List of filtered resumes"
            ),
        }
    )
)


@swagger_auto_schema(
    method='get',
    query_serializer=ResumeFilterSerializer(),
    responses={
        200: success_response,  
        400: validation_error_response,  
        500: server_error_response 
    }
)
@api_view(['GET'])
def retrieve_data_view(request):
    try:
        serializer = ResumeFilterSerializer(data=request.query_params)

        if serializer.is_valid():
            params = serializer.validated_data
            
            result = ResumeController.filter_resume(params, request)
            return result  

        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    except ValidationError as e:
        return Response({"error": "Validation error", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)