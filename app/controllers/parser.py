from resumeparser.settings import logger
from app.models import Resume
import PyPDF2
from app.api_books import extract_info_from_resume
from resumeparser.settings import collection
from app.constants import StatusMessages
from app.exceptions import ResumeTextExtractionError, ResumeParsingError, ResumeSaveError


class ResumeController:

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
        except FileNotFoundError:
            logger.error(f"The file {pdf_path} was not found.", exc_info=True)
            raise ResumeTextExtractionError(f"The file {pdf_path} was not found.")
        except PyPDF2.errors.PdfReadError:
            logger.error(f"The file {pdf_path} is not a valid PDF.", exc_info=True)
            raise ResumeTextExtractionError(f"The file {pdf_path} is not a valid PDF.")
        except Exception as e:
            logger.error(f"An error occurred while reading the PDF: {e}", exc_info=True)
            raise ResumeTextExtractionError(f"An unexpected error occurred while reading the PDF: {e}")

    @staticmethod
    def extract_resume_category(data):
        return data.get("resume_type", None)

    @staticmethod
    def process_resume(instance):
        instance.set_file_location()
        resume_text = ResumeController.extract_text_from_pdf(instance.get_file_location())

        if resume_text is None:
            raise ResumeParsingError("Failed to extract text from the resume.")

        parsed_data = extract_info_from_resume(resume_text)

        if parsed_data is None:
            raise ResumeParsingError("Failed to parse data from the resume.")

        try:
            mongo_doc_id = collection.insert_one({
                'parsed_data': parsed_data
            }).inserted_id

            instance.update(parsed_data_id=mongo_doc_id, resume_category=ResumeController.extract_resume_category(parsed_data), parsing_status='completed')
            instance.save()
        except Exception as e:
            logger.error(f"Error saving instance: {e}", exc_info=True)
            raise ResumeSaveError(f"Failed to save resume data: {e}")

        logger.info(StatusMessages.SUCCESS)
        return {"message": StatusMessages.SUCCESS, "data": parsed_data}
