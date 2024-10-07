from resumeparser.settings import logger
from app.models import Resume
import pdfplumber
from app.api_books import extract_info_from_resume
from resumeparser.settings import collection
from app.constants import StatusMessages
from app.exceptions import ResumeTextExtractionError, ResumeParsingError, ResumeSaveError
from bs4 import BeautifulSoup 
import re
import string
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')


class ResumeController:

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except FileNotFoundError:
            logger.error(f"The file {pdf_path} was not found.", exc_info=True)
            raise ResumeTextExtractionError(f"The file {pdf_path} was not found.")
        except Exception as e:
            logger.error(f"An error occurred while reading the PDF: {e}", exc_info=True)
            raise ResumeTextExtractionError(f"An unexpected error occurred while reading the PDF: {e}")

    @staticmethod
    def remove_html_tags(text):
        return BeautifulSoup(text, "html.parser").get_text()

    @staticmethod
    def remove_punctuation(text):
        return text.translate(str.maketrans('', '', string.punctuation))

    @staticmethod
    def remove_stop_words(text):
        stop_words = set(stopwords.words('english'))
        words = text.split()
        filtered_words = [word for word in words if word not in stop_words]
        return ' '.join(filtered_words)

    @staticmethod
    def extract_resume_category(data):
        return data.get("resume_type", None)

    @staticmethod
    def process_resume(instance):
        instance.set_file_location()
        resume_text = ResumeController.extract_text_from_pdf(instance.get_file_location())

        if resume_text is None:
            raise ResumeParsingError("Failed to extract text from the resume.")

        resume_text = resume_text.lower()  
        resume_text = ResumeController.remove_html_tags(resume_text) 
        resume_text = ResumeController.remove_punctuation(resume_text) 
        resume_text = ResumeController.remove_stop_words(resume_text) 

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
