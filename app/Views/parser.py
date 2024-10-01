from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework import status
from app.models.parser import Resume
from app.serializers.parser import ResumeSerializer
from app.controllers.parser import ResumeController


class ResumeUploadView(ListCreateAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resume_instance = serializer.save()
        result = ResumeController.process_resume(resume_instance)

        return Response(result, status=status.HTTP_201_CREATED)
