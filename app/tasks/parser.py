from resumeparser.settings import logger
from celery import shared_task
from app.models import Resume
from app.controllers import ResumeController
from celery.exceptions import MaxRetriesExceededError
from app.constants import StatusMessages
from app.exceptions import ResumeProcessingError


@shared_task(bind=True, max_retries=3)
def process_resume_task(self, resume_ids):
    try:
        if not resume_ids:
            logger.error("No resume IDs provided for processing.", exc_info=True)
            return

        resumes = Resume.get_all(resume_ids)
        for resume in resumes:
            logger.info(f'Processing resume: {resume.id}')

            result = ResumeController.process_resume(resume)

            if result.get('message') != StatusMessages.SUCCESS:
                logger.error(f'Resume processing failed for: {resume.id}', exc_info=True)
                raise ResumeProcessingError(f'Resume processing failed for {resume.id}')
            
            logger.info(f'Resume processed successfully: {resume.id}')

        return {"message": "Bulk resume processing completed successfully."}

    except ResumeProcessingError as exc:
        logger.error(f'Error processing resumes: {exc}', exc_info=True)
        
        retry_intervals = [300, 600, 1800]
        retry_count = self.request.retries
        retry_countdown = retry_intervals[retry_count] if retry_count < len(retry_intervals) else retry_intervals[-1]

        logger.exception(f'Retrying in {retry_countdown // 60} minutes...', exc_info=True)
        self.retry(exc=exc, countdown=retry_countdown)

    except MaxRetriesExceededError:
        logger.error(f'Max retries exceeded for resumes', exc_info=True)
        for resume_id in resume_ids:
            Resume.get(resume_id).update(parsing_status="failed")
