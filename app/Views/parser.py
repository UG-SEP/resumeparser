from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.tasks import process_resume_task
from app.serializers import ResumeSerializer
from app.models import Resume
from app.controllers import ResumeController
from resumeparser.settings import logger

@api_view(['POST', 'GET'])
def resume_upload_view(request):
    logger.info(f"Received request method: {request.method}, path: {request.path}")
    
    if request.method == 'POST':
        resume_files = request.FILES.getlist('resumes')
        
        if not resume_files:
            return Response({"error": "No files uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Extract the validated_data extract the instance_info and convert it into dict / json and then bulk save 
        # and pass to the process_resume_task
        serializer = ResumeSerializer()
        created_resumes = serializer.create_bulk(resume_files) 
        resume_ids = [str(resume.id) for resume in created_resumes]       
        process_resume_task.delay(resume_ids)
        logger.info(f"{len(resume_files)} Resume has been passed to the celery task for background processing: ")
        return Response(
            {"message": f"{len(resume_files)} resumes uploaded and processing started."},
            status=status.HTTP_201_CREATED
        )

    elif request.method == 'GET':
        try:
            #TODO : Donot pass the request directly used serializer to serializer the data and then pass and take request as optimal
            result = ResumeController.filter_resume(request)
            return result
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
