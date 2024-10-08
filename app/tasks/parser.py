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
        resume_instance = Resume.get(resume_id)

        if not resume_instance:
            logger.error(f"Resume {resume_id} not found.", exc_info=True)
            return

        logger.info(f'Processing resume: {resume_instance.id}')

        result = ResumeController.process_resume(resume_instance)

        if result.get('message') != StatusMessages.SUCCESS:
            logger.error(f'Resume processing failed for: {resume_instance.id}', exc_info=True)
            raise ResumeProcessingError('Resume processing failed')

        logger.info(f'Resume processed successfully: {resume_instance.id}')
        return result

    except ResumeProcessingError as exc:
        logger.error(f'Error processing resume: {resume_id} - {str(exc)}', exc_info=True)
        if resume_instance:
            resume_instance.update_retry()

        retry_intervals = [300, 600, 1800]
        retry_count = self.request.retries
        retry_countdown = retry_intervals[retry_count] if retry_count < len(retry_intervals) else retry_intervals[-1]

        logger.exception(f'Retrying in {retry_countdown // 60} minutes...', exc_info=True)
        self.retry(exc=exc, countdown=retry_countdown)

    except MaxRetriesExceededError:
        logger.error(f'Max retries exceeded for resume: {resume_id}', exc_info=True)
        if resume_instance:
            resume_instance.update(parsing_status="failed")

@shared_task
def filter_resume_task(self,request):
    return ResumeController.filter_resume(request)