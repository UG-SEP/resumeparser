from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from app.models import Resume
from app.serializers import ResumeSerializer

class ResumeApiTests(APITestCase):
    def setUp(self):
        self.upload_url = reverse('resume-upload')  # Adjust based on your URL routing
        self.retrieve_url = reverse('retrieve-data')  # Adjust based on your URL routing

    def test_resume_upload_success(self):
        """Test the resume upload endpoint with valid files."""
        with open('U:/drive-download-20241009T182740Z-001 - Copy', 'rb') as resume_file:
            response = self.client.post(self.upload_url, {'file': resume_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertTrue("resumes uploaded and processing started." in response.data["message"])

    def test_resume_upload_no_files(self):
        """Test the resume upload endpoint with no files."""
        response = self.client.post(self.upload_url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "No files uploaded.")

    def test_retrieve_data_success(self):
        """Test the retrieve data endpoint with valid query parameters."""
        # Assuming you have some resumes saved in your database
        # You may want to create resumes in setUp or here
        resume = Resume.objects.create(...)  # Fill in the required fields

        # Add appropriate query parameters based on your filter serializer
        params = {
            "format_type": "csv"
        }
        response = self.client.get(self.retrieve_url, params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("data", response.data)

    def test_retrieve_data_validation_error(self):
        """Test the retrieve data endpoint with invalid query parameters."""
        params = {
            'invalid_field': 'value',
        }
        response = self.client.get(self.retrieve_url, params)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", response.data)

    def test_retrieve_data_server_error(self):
        """Test the retrieve data endpoint to simulate a server error."""
        # You may want to mock or alter some conditions to force an error
        response = self.client.get(self.retrieve_url)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("error", response.data)

