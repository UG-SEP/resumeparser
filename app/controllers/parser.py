import logging
from app.models import Resume
import PyPDF2
import os 
from app.api_books import extract_info_from_resume

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
            logger.error(f"The file {pdf_path} was not found.")
            return None
        except PyPDF2.errors.PdfReadError:
            logger.error(f"The file {pdf_path} is not a valid PDF.")
            return None
        except Exception as e:
            logger.error(f"An error occurred while reading the PDF: {e}")
            return None
            
    @staticmethod 
    def extract_resume_category(data):
        return data["Personal Information"].get("Resume Category", None)

    @staticmethod
    def process_resume(instance):
        instance.storage_path = instance.file.path
        resume_text = ResumeController.extract_text_from_pdf(instance.storage_path)
        
        if resume_text is None:
            return {"message": "Failed to extract text from the PDF."}
        
        parsed_data = extract_info_from_resume(resume_text)
        
        if parsed_data is None:
            return {"message": "Failed to parse resume data."}

        instance.resume_category = ResumeController.extract_resume_category(parsed_data)
        instance.parsing_status = 'completed'
        
        try:
            instance.save()
        except Exception as e:
            logger.error(f"Error saving instance: {e}")
            return {"message": "Failed to save resume data."}
        
        logger.info("Resume processed successfully")
        return {"message": "Resume processed successfully", "data": parsed_data}
