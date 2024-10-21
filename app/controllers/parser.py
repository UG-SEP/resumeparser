from asyncio import sleep
import time
from resumeparser.settings import logger
from app.models import Resume
import pdfplumber
from app.api_books import extract_info_from_resume
from resumeparser.settings import collection
from app.constants import StatusMessages
from app.exceptions import ResumeProcessingError, ResumeTextExtractionError, ResumeParsingError, ResumeSaveError
from bs4 import BeautifulSoup 
import re
import string
import nltk
from nltk.corpus import stopwords
from app.pagination import ResumePagination
from rest_framework.response import Response
from rest_framework import status
import csv
from django.http import HttpResponse
import json
from .query_helper import *
from .csv_helper import *
from pymongo import ReturnDocument
from .helper import decorate_csv
import fitz


nltk.download('stopwords')


class ResumeController:

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_number, page in enumerate(pdf.pages):
                    page_text = page.extract_text()

                    time.sleep(1)
                    if not page_text:
                        # Log and handle empty page cases
                        logger.error(f"Page {page_number + 1} returned empty text.")
                    else:
                        text += page_text + "\n"
            return text.strip()
        except FileNotFoundError:
            logger.error(f"The file {pdf_path} was not found.", exc_info=True)
            raise ResumeTextExtractionError(f"The file {pdf_path} was not found.")
        except Exception as e:
            logger.error(f"An error occurred while reading the PDF: {e}", exc_info=True)
            raise ResumeTextExtractionError(f"An unexpected error occurred while reading the PDF: {e}")

    # @staticmethod
    # def remove_html_tags(text):
    #     return BeautifulSoup(text, "html.parser").get_text()

    # @staticmethod
    # def remove_punctuation(text):
    #     return text.translate(str.maketrans('', '', string.punctuation))

    @staticmethod
    def extract_email(resume_text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.findall(email_pattern, resume_text)
        return email_match[0] if email_match else None
    @staticmethod
    def extract_mobile(resume_text):
        mobile_pattern =  r'\+?\d{1,3}[-.\s]?\d{1,5}[-.\s]?\d{3,5}[-.\s]?\d{3,5}'
        mobile_match = re.findall(mobile_pattern, resume_text)
        return mobile_match[0] if mobile_match else None

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
    def extract_urls_from_pdf(pdf_path):
        try:
            doc = fitz.open(pdf_path)
            urls = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                links = page.get_links()
                
                for link in links:
                    uri = link.get('uri')
                    if uri:
                        urls.append(uri)
            return urls
        except Exception as e:
            logger.error(f"An error occurred while extracting URLs from the PDF: {e}")
            raise ResumeTextExtractionError(f"Failed to extract URLs from the PDF: {e}")

    @staticmethod
    def extract_linkedin_and_github(urls):
        linkedin_url = None
        github_url = None
        mailto_url = None

        linkedin_pattern = r"(https?:\/\/)?(www\.)?linkedin\.com\/in\/[a-zA-Z0-9\-]+\/?"
        github_pattern = r"(https?:\/\/)?(www\.)?github\.com\/[a-zA-Z0-9\-]+\/?$"
        mailto_pattern = r"mailto:([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"


        for url in urls:
            if re.search(linkedin_pattern, url):
                linkedin_url = url
            if re.search(github_pattern, url):
                github_url = url
            mailto_match = re.search(mailto_pattern, url)
            if mailto_match:
                mailto_url = mailto_match.group(1)

        return linkedin_url, github_url, mailto_url

    @staticmethod 
    def validate_email(email):
        email_validation_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(email_validation_pattern, email) is not None
    @staticmethod
    def process_resume(resume_id):
        try:
            
            resume = Resume.get(resume_id)
            logger.info(f"Processing resume: {resume_id}")
            if not resume.id:
                raise ResumeProcessingError(f"Resume {resume_id} does not exist.")

            resume.set_file_location()
            file_location = resume.get_file_location()
            resume_text =  ResumeController.extract_text_from_pdf(file_location)
            logger.info(f"Extracted text from the resume: {resume_text}")
            resume_text = resume_text.lower()  
            resume_text = ResumeController.remove_stop_words(resume_text)

            if resume_text is None:
                raise ResumeParsingError(f"Failed to extract text from the resume: {resume_id}")  
            
            
            logger.info(f"Sending resume {resume_id} for parsing to openai.")
            parsed_data = extract_info_from_resume(resume_text) 
            logger.info(f"Received parsed data from openai: {parsed_data} for resume: {resume_id}")
            if parsed_data is None:
                # import pdb
                # pdb.set_trace()
                raise ResumeParsingError(f"Failed to parse data from the resume: {resume_id}")
        
        except Exception as e:
            logger.error(f"Error processing resume: {e}", exc_info=True)
            # import pdb
            # pdb.set_trace()
            raise ResumeProcessingError(f"Failed to process resume: {e}")


        try:
            email = ResumeController.extract_email(resume_text)
            mobile = ResumeController.extract_mobile(resume_text)
            urls = ResumeController.extract_urls_from_pdf(file_location)
            linkedin_url, github_url, mailto_url = ResumeController.extract_linkedin_and_github(urls)

            if linkedin_url is not None:
                parsed_data['personal_information']['linkedin'] = linkedin_url

            if github_url is not None:
                parsed_data['personal_information']['github'] = github_url

            if email is not None and mobile is not None:
                parsed_data['personal_information']['email'] = email
                parsed_data['personal_information']['mobile'] = mobile
            
            elif mailto_url is not None:
                parsed_data['personal_information']['email'] = mailto_url
            
            if ResumeController.validate_email(parsed_data['personal_information']['email']) == None:
                return {"message": StatusMessages.EMAIL_NOT_FOUND}

            if parsed_data['personal_information']['email']:
                existing_document = collection.find_one({"parsed_data.personal_information.email": email})
                
                if existing_document:
                    mongo_doc_id = collection.find_one_and_update(
                        {"parsed_data.personal_information.email": email},  
                        {"$set": {'parsed_data': parsed_data}}, 
                        return_document=ReturnDocument.AFTER
                    ).get('_id')
                    
                    logger.info(f"Updated existing document with ID: {mongo_doc_id}")

                else:
                    mongo_doc_id = collection.insert_one({
                        'parsed_data': parsed_data
                    }).inserted_id
                    
                    logger.info(f"Inserted new document with ID: {mongo_doc_id}")
                
                resume.update(
                    parsed_data_id=mongo_doc_id, 
                    resume_category=ResumeController.extract_resume_category(parsed_data), 
                    parsing_status='completed'
                )
                resume.save()
            
            else:
                raise ValueError("Email not found in parsed_data")

        except Exception as e:
            logger.error(f"Error saving instance: {e}", exc_info=True)
            raise ResumeSaveError(f"Failed to save resume data: {e}")

        logger.info(StatusMessages.SUCCESS)
        logger.info(parsed_data)
        resume.delete_file()
        return {"message": StatusMessages.SUCCESS, "data": parsed_data}
    
    # @staticmethod
    # def extract_query_params(request):
    #     return {
    #         "skills_experience": request.query_params.get('skills_experience',None),
    #         "skills_and": request.query_params.get('skills_and',None),
    #         "proficient_technologies_and": request.query_params.get('proficient_technologies_and',None),
    #         "full_time_experience": request.query_params.get('full_time_experience', None),
    #         "company_type": request.query_params.get('company_type', None),
    #         "product_company_experience": request.query_params.get('product_company_experience', None),
    #         "startup_experience": request.query_params.get('startup_experience', None),
    #         "degree_type": request.query_params.get('degree_type', None),
    #         "last_position_held": request.query_params.get('last_position_held', None),
    #         "gen_ai_experience": request.query_params.get('gen_ai_experience', None),
    #         "is_cs_degree": request.query_params.get('is_cs_degree', None),
    #         "is_ml_degree": request.query_params.get('is_ml_degree', None),
    #         "early_stage_startup_experience": request.query_params.get('early_stage_startup_experience', None),
    #         "institute_type": request.query_params.get('institute_type', None),
    #         "llm_experience": request.query_params.get('llm_experience', None),
    #         "service_company_experience": request.query_params.get('service_company_experience', None),
    #         "resume_type": request.query_params.get('resume_type', None),
    #         "projects_outside_of_work": request.query_params.get('projects_outside_of_work', None),
    #         "time_filter": request.query_params.get('time_filter',None),
    #         "skills_or": request.query_params.get('skills_or',None),
    #         "proficient_technologies_or" : request.query_params.get('proficient_technologies_or',None)
    #     }

    @staticmethod #TODO move to utils/helpers
    def build_filter_query(params):
        filter_query = {}

        full_time_experience_query(params,filter_query)
        skills_experience_query(params,filter_query)
        company_type_query(params,filter_query)
        product_company_experience_query(params,filter_query)
        startup_experience_query(params,filter_query)
        degree_type_query(params,filter_query)
        last_position_held_query(params,filter_query)
        gen_ai_experience_query(params,filter_query)
        is_ml_degree_query(params,filter_query)
        is_cs_degree_query(params,filter_query)
        early_stage_startup_experience_query(params,filter_query)
        institute_type_query(params,filter_query)
        llm_experience_query(params,filter_query)
        service_company_experience_query(params,filter_query)
        resume_type_query(params,filter_query)
        projects_outside_of_work_query(params,filter_query)
        skills_and_query(params,filter_query)
        proficient_technologies_and_query(params,filter_query)
        skills_or_query(params,filter_query)
        proficient_technologies_or_query(params,filter_query)
        one_hour_filter(params,filter_query)
        six_hour_filter(params,filter_query)
        tweleve_hour_filter(params,filter_query)
        one_day_filter(params,filter_query)
        seven_day_filter(params,filter_query)
        one_month_filter(params,filter_query)
        print(filter_query)
        return filter_query

    @staticmethod
    def filter_resume(params, request=None):
        try:
            filter_query = ResumeController.build_filter_query(params)

            try:
                resumes = list(collection.find(filter_query))
                print(resumes)
                decorate_csv(resumes)
            except Exception as e:
                logger.error(f"Database query failed: {e}", exc_info=True)
                raise ValueError("Database error occurred while querying resumes.")

            if not resumes:
                return Response({"message": "No resumes found matching the criteria."}, status=status.HTTP_204_NO_CONTENT)

            for resume in resumes:
                resume["_id"] = str(resume["_id"])

            if request and request.query_params.get('format_type') == 'csv':
                return ResumeController.generate_csv_response(resumes)

            paginated_resumes = None
            if request:
                paginator = ResumePagination()
                paginated_resumes = paginator.paginate_queryset(resumes, request)

            if paginated_resumes is not None:
                return paginator.get_paginated_response(paginated_resumes)
            
            return Response(resumes, status=status.HTTP_200_OK)

        except ValueError as e:
            logger.error(f"Error filtering resumes: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Unexpected error in filtering resumes: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @staticmethod
    def generate_csv_response(resumes):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resumes.csv"'
        writer = csv.writer(response)
        headers = []
        personal_info_headers(headers)
        skills_headers(headers)
        education_headers(headers)
        experience_headers(headers)
        project_headers(headers)
        additional_experience_summary_headers(headers)
        overall_summary_headers(headers)
        parsed_data_header(headers)

        writer.writerow(headers)
        
        for resume in resumes:
            row = []
            parsed_data = resume.get('parsed_data', {})
            personal_info_data(parsed_data,row)
            skills_data(parsed_data,row)
            educations_data(parsed_data,row)
            experience_data(parsed_data,row)
            project_data(parsed_data,row)
            additional_experience_summary_data(parsed_data,row)
            overall_summary_data(parsed_data,row)
            json_data(parsed_data,row)

            writer.writerow(row)

        return response
