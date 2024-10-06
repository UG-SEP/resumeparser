from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.models import Resume
from app.serializers import ResumeSerializer
from app.tasks import process_resume_task  

@api_view(['POST', 'GET'])
def resume_upload_view(request):
    if request.method == 'POST':
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            resume_instance = serializer.save()
            process_resume_task.delay(resume_instance.id)
            return Response({"message": "Resume upload successful. Processing in background."}, status=status.HTTP_201_CREATED)
        

    elif request.method == 'GET':
        resumes = Resume.objects.all()
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)
