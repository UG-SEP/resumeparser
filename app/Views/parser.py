from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.tasks import process_resume_task
from resumeparser.settings import collection
from app.serializers import ResumeSerializer
from app.controllers import ResumeController

@api_view(['POST', 'GET'])
def resume_upload_view(request):
    if request.method == 'POST':
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            resume_instance = serializer.save()
            process_resume_task.delay(resume_instance.id)
            return Response({"message": "Resume upload successful. Processing in background."}, status=status.HTTP_201_CREATED)

    elif request.method == 'GET':
        try:
            result = ResumeController.filter_resume(request)
            return result
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
