import os
import requests
from resumeparser.settings import logger
from celery import shared_task
from app.models import Resume
from app.controllers import ResumeController
from celery.exceptions import MaxRetriesExceededError
from app.constants import StatusMessages
from app.exceptions import ResumeProcessingError

@shared_task(bind=True, max_retries=3)
def process_resume_task(self, resume_id):
    try:
        if not resume_id:
            logger.error("No resume ID provided for processing.", exc_info=True)
            return

        resume = Resume.get(resume_id)        
        s3_url = resume.s3_file_location
        local_directory = "media/resumes"
        os.makedirs(local_directory, exist_ok=True)
        local_path = os.path.join(local_directory, f"{resume.id}.pdf")

        try:
            response = requests.get(s3_url, stream=True)
            response.raise_for_status()
            
            with open(local_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            resume.set_file_location(local_path)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download resume {resume.id} from S3: {str(e)}", exc_info=True)
            return  

        result = ResumeController.process_resume(resume.id)

        if result.get('message') != StatusMessages.SUCCESS:
            logger.error(f'Resume processing failed for: {resume.id}', exc_info=True)
            raise ResumeProcessingError(f'Resume processing failed for {resume.id}')
        
        logger.info(f'Resume processed successfully: {resume.id}')
        return {"message": "Resume processed successfully."}

    except ResumeProcessingError as exc:
        logger.error(f'Error processing resume: {exc}', exc_info=True)
        
        retry_intervals = [300, 600, 1800]
        retry_count = self.request.retries
        retry_countdown = retry_intervals[retry_count] if retry_count < len(retry_intervals) else retry_intervals[-1]

        logger.exception(f'Retrying in {retry_countdown // 60} minutes...', exc_info=True)
        self.retry(exc=exc, countdown=retry_countdown)

    except MaxRetriesExceededError:
        logger.error(f'Max retries exceeded for resume {resume_id}', exc_info=True)
        Resume.get(resume_id).update(parsing_status="failed")
