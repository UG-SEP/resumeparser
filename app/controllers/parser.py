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
from app.pagination import ResumePagination

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
        
        

        parsed_data = extract_info_from_resume(resume_text)
        # parsed_data = resume_text.lower()  
        # parsed_data = ResumeController.remove_html_tags(parsed_data) 
        # parsed_data = ResumeController.remove_punctuation(parsed_data) 
        # parsed_data = ResumeController.remove_stop_words(parsed_data) 
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
    
    @staticmethod
    def extract_query_params(request):
        """Extract query parameters from the request."""
        return {
            "skills": request.query_params.getlist('skills', []),
            "min_experience": request.query_params.get('experience', None),
            "technologies": request.query_params.getlist('technologies', []),
            "company_type": request.query_params.get('company_type', None),
            "product_company_exp": request.query_params.get('product_company_experience', None),
            "startup_exp": request.query_params.get('startup_experience', None),
            "degree_type": request.query_params.get('degree_type', None),
            "position": request.query_params.get('position', None),
            "gen_ai_exp": request.query_params.get('gen_ai_experience', None),
            "four_year_cs_degree": request.query_params.get('four_year_cs_degree', None),
            "early_stage_startup_exp": request.query_params.get('early_stage_startup_exp', None),
        }

    @staticmethod
    def validate_query_params(params):
        """Validate the query parameters extracted from the request."""
        if params['min_experience'] and not params['min_experience'].isdigit():
            raise ValueError("Experience should be a valid number.")
        if params['product_company_exp'] and not params['product_company_exp'].isdigit():
            raise ValueError("Product company experience should be a valid number.")
        if params['startup_exp'] and not params['startup_exp'].isdigit():
            raise ValueError("Startup experience should be a valid number.")
        if params['early_stage_startup_exp'] and not params['early_stage_startup_exp'].isdigit():
            raise ValueError("Early stage startup experience should be a valid number.")

    @staticmethod
    def build_filter_query(params):
        """Build the filter query based on the provided parameters."""
        filter_query = {}

        if params['skills']:
            filter_query["parsed_data.Skills.Languages"] = {"$all": params['skills']}

        if params['min_experience']:
            filter_query["parsed_data.Skills.Total Skill Experience.Python"] = {
                "$regex": f"{params['min_experience']}\\+ years", "$options": "i"
            }

        if params['technologies']:
            filter_query["parsed_data.Skills.Technologies"] = {"$all": params['technologies']}

        if params['company_type']:
            filter_query["parsed_data.Experience.Company Information.Company Type"] = params['company_type']

        if params['product_company_exp']:
            filter_query["parsed_data.product_company_experience"] = {"$gte": int(params['product_company_exp'])}

        if params['startup_exp']:
            filter_query["parsed_data.total_startup_experience"] = {"$gte": int(params['startup_exp'])}

        if params['degree_type']:
            filter_query["parsed_data.Education.Degree Name"] = {"$regex": params['degree_type'], "$options": "i"}

        if params['position']:
            filter_query["parsed_data.Experience.Company Information.Last Position Held"] = params['position']

        if params['gen_ai_exp']:
            filter_query["parsed_data.Skills.Gen AI Experience"] = params['gen_ai_exp'].lower() == 'true'

        if params['four_year_cs_degree']:
            filter_query["parsed_data.Education.Is CS Degree"] = params['four_year_cs_degree'].lower() == 'true'

        if params['early_stage_startup_exp']:
            filter_query["parsed_data.total_early_stage_startup_experience"] = {"$gte": int(params['early_stage_startup_exp'])}

        return filter_query

    @staticmethod
    def filter_resume(request):
        try:
            query_params = ResumeController.extract_query_params(request)

            ResumeController.validate_query_params(query_params)

            filter_query = ResumeController.build_filter_query(query_params)

            try:
                resumes = list(collection.find(filter_query))
            except Exception as e:
                logger.error(f"Database query failed: {e}", exc_info=True)
                raise ValueError("Database error occurred while querying resumes.")

            if not resumes:
                return Response({"message": "No resumes found matching the criteria."}, status=status.HTTP_204_NO_CONTENT)

            for resume in resumes:
                resume["_id"] = str(resume["_id"])

            paginator = ResumePagination()
            paginated_resumes = paginator.paginate_queryset(resumes, request)

            return paginator.get_paginated_response(paginated_resumes)

        except ValueError as e:
            logger.error(f"Error filtering resumes: {str(e)}", exc_info=True)
            raise e
        except Exception as e:
            logger.error(f"Unexpected error in filtering resumes: {str(e)}", exc_info=True)
            raise e