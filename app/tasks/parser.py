import logging
from celery import shared_task
from app.models import Resume
from app.controllers import ResumeController
from celery.exceptions import MaxRetriesExceededError
from app.constants import StatusMessages

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3) 
def process_resume_task(self, resume_id):
    try:
        resume_instance = Resume.objects.get(id=resume_id)
        logger.info(f'Processing resume: {resume_instance.id}')
        
        result = ResumeController.process_resume(resume_instance)

        if result.get('message') != StatusMessages.SUCCESS:
            logger.error(f'Resume processing failed for: {resume_instance.id}')
            raise Exception('Resume processing failed')

        logger.info(f'Resume processed successfully: {resume_instance.id}')
        return result

    except Exception as exc:
        try:
            resume_instance.no_of_retries+=1
            resume_instance.save()
            retry_intervals = [300, 600, 1800]
            retry_countdown = retry_intervals[self.request.retries]

            logger.exception(f'Error processing resume: {resume_id}. Retrying in next {retry_countdown // 60} minutes...') 
            self.retry(exc=exc, countdown=retry_countdown)

        except MaxRetriesExceededError:
            logger.error(f'Max retries exceeded for resume: {resume_id}')
            resume_instance.parsing_status = "failed"
            resume_instance.save()
            raise Exception("Max retries exceeded for resume processing") from exc