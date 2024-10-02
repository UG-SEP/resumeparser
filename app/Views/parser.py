from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from app.models import Resume
from app.serializers import ResumeSerializer
from app.controllers import ResumeController




@api_view(['POST', 'GET'])
def resume_upload_view(request):
    if request.method == 'POST':
        serializer = ResumeSerializer(data=request.data)
        if serializer.is_valid():
            resume_instance = serializer.save()
            result = ResumeController.process_resume(resume_instance)
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        resumes = Resume.objects.all()
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data)
