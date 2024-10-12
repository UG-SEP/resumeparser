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

nltk.download('stopwords')


class ResumeController:

    @staticmethod
    def extract_text_from_pdf(pdf_path):
        try:
            # import pdb; pdb.set_trace()
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
    def process_resume(resume_id):
        try:
            # import pdb; pdb.set_trace()
            resume = Resume.get(resume_id)
            logger.info(f"Processing resume: {resume_id}")
            if not resume.id:
                raise ResumeProcessingError(f"Resume {resume_id} does not exist.")

            resume.set_file_location()
            file_location = resume.get_file_location()
            resume_text =  ResumeController.extract_text_from_pdf(file_location)
            logger.info(f"Extracted text from the resume: {resume_text}")
            # sleep(5)
            resume_text = resume_text.lower()  
            resume_text = ResumeController.remove_html_tags(resume_text) 
            resume_text = ResumeController.remove_punctuation(resume_text) 
            resume_text = ResumeController.remove_stop_words(resume_text)

            if resume_text is None:
                raise ResumeParsingError(f"Failed to extract text from the resume: {resume_id}")  
            
            
            logger.info(f"Sending resume {resume_id} for parsing to openai.")
            parsed_data = extract_info_from_resume(resume_text) 
            logger.info(f"Received parsed data from openai: {parsed_data} for resume: {resume_id}")
            if parsed_data is None:
                raise ResumeParsingError(f"Failed to parse data from the resume: {resume_id}")
        
        except Exception as e:
            logger.error(f"Error processing resume: {e}", exc_info=True)
            raise ResumeProcessingError(f"Failed to process resume: {e}")


        try:
            mongo_doc_id = collection.insert_one({
                'parsed_data': parsed_data
            }).inserted_id
            resume.update(parsed_data_id=mongo_doc_id, resume_category=ResumeController.extract_resume_category(parsed_data), parsing_status='completed')
            resume.save()
        except Exception as e:
            logger.error(f"Error saving instance: {e}", exc_info=True)
            raise ResumeSaveError(f"Failed to save resume data: {e}")

        logger.info(StatusMessages.SUCCESS)
        return {"message": StatusMessages.SUCCESS, "data": parsed_data}
    
    @staticmethod
    def extract_query_params(request):
        return {
            "skills_experience": request.query_params.get('skills_experience',None),
            "skills": request.query_params.get('skills',None),
            "proficient_technologies": request.query_params.get('proficient_technologies',None),
            "full_time_experience": request.query_params.get('full_time_experience', None),
            "company_type": request.query_params.get('company_type', None),
            "product_company_experience": request.query_params.get('product_company_experience', None),
            "startup_experience": request.query_params.get('startup_experience', None),
            "degree_type": request.query_params.get('degree_type', None),
            "last_position_held": request.query_params.get('last_position_held', None),
            "gen_ai_experience": request.query_params.get('gen_ai_experience', None),
            "is_cs_degree": request.query_params.get('is_cs_degree', None),
            "is_ml_degree": request.query_params.get('is_ml_degree', None),
            "early_stage_startup_experience": request.query_params.get('early_stage_startup_experience', None),
            "institute_type": request.query_params.get('institute_type', None),
            "llm_experience": request.query_params.get('llm_experience', None),
            "service_company_experience": request.query_params.get('service_company_experience', None),
            "resume_type": request.query_params.get('resume_type', None),
            "projects_outside_of_work": request.query_params.get('projects_outside_of_work', None),
        }

    @staticmethod #TODO move to utils/helpers
    def build_filter_query(params):
        filter_query = {}

        if params.get('full_time_experience'):
            filter_query["parsed_data.additional_experience_summary.years_of_full_time_experience_after_graduation"] = {
                "$gte": int(params['full_time_experience'])
            }
        
        if params.get('skills_experience'):
            skills = split_and_strip(params, "skills_experience")

            skill_queries = []
            for skill in skills:
                skill_name, experience_years = skill.split('|')
                experience_years = int(experience_years)

                skill_query = {
                    f"parsed_data.skills.total_skill_experience.{skill_name}": {
                        "$gte": experience_years
                    }
                }
                skill_queries.append(skill_query)

            if skill_queries:
                filter_query["$or"] = skill_queries


        if params.get('company_type') == 'product':
            filter_query["parsed_data.additional_experience_summary.product_company_experience"] = {
                "$gt": 0
            }

        if params.get('company_type') == 'startup':
            filter_query["parsed_data.additional_experience_summary.total_startup_experience"] = {
                "$gt": 0 
            }

        if params.get('product_company_experience'):
            filter_query["parsed_data.additional_experience_summary.product_company_experience"] = {
                "$gte": int(params['product_company_experience'])
            }

        if params.get('startup_experience'):
            filter_query["parsed_data.additional_experience_summary.total_startup_experience"] = {
                "$gte": int(params['startup_experience'])
            }

        if params.get('degree_type'):
            filter_query["parsed_data.education.degree_level"] = {
                "$regex": f"^{params['degree_type']}$", "$options": "i"
            }

        if params.get('last_position_held'):
            filter_query["parsed_data.additional_experience_summary.last_position_held"] = {
                "$regex": f".*{re.escape(params['last_position_held'])}.*",
                "$options": "i"
            }


        if params.get('gen_ai_experience'):
            filter_query["parsed_data.skills.gen_ai_experience"] = params['gen_ai_experience'].lower() == 'true'
        
        if params.get('is_ml_degree'):
            filter_query["parsed_data.education.is_ml_degree"] = params['is_ml_degree'].lower() == 'true'

        if params.get('is_cs_degree'):
            filter_query["parsed_data.education.is_cs_degree"] = params['is_cs_degree'].lower() == 'true'

        if params.get('early_stage_startup_experience'):
            filter_query["parsed_data.additional_experience_summary.total_early_stage_startup_experience"] = {
                "$gte": int(params['early_stage_startup_experience'])
            }

        if params.get('institute_type'):
            filter_query["parsed_data.education.institute_type"] = {
            "$regex": f"^{re.escape(params['institute_type'])}$",
            "$options": "i"  
        }

        if params.get('llm_experience'):
            filter_query["parsed_data.skills.llm_experience"] = params['llm_experience'].lower() == 'true'

        if params.get('service_company_experience'):
            filter_query["parsed_data.additional_experience_summary.service_company_experience"] = {
                "$gte": int(params['service_company_experience'])
            }

        if params.get('resume_type'):
            filter_query["parsed_data.resume_type"] = {
                "$regex": f"^{params['resume_type']}$", "$options": "i"
            }

        if params.get('projects_outside_of_work'):
            filter_query["parsed_data.projects_outside_of_work"] = {"$exists": True, "$ne": []}
        
        if params.get('skills'):
            skills = split_and_strip(params,'skills')
            if skills:
                pattern = '|'.join(map(re.escape, skills))
                filter_query.update({
                    "$or": [
                        {
                            "parsed_data.skills.technologies.proficient": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        },
                        {
                            "parsed_data.skills.languages.proficient": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        },
                        {
                            "parsed_data.skills.frameworks.proficient": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        },
                        {
                            "parsed_data.skills.frameworks.average": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        },
                        {
                            "parsed_data.skills.languages.average": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        },
                        {
                            "parsed_data.skills.technologies.average": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        }
                    ]
                })


        if params.get('proficient_technologies'):
            proficient_technologies = split_and_strip(params, 'proficient_technologies')
            if proficient_technologies:
                pattern = '|'.join(map(re.escape, proficient_technologies))

                filter_query.update({
                    "$or": [
                        {
                            "parsed_data.skills.technologies.proficient": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        },
                        {
                            "parsed_data.skills.languages.proficient": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        },
                        {
                            "parsed_data.skills.frameworks.proficient": {
                                "$regex": pattern,
                                "$options": "i"
                            }
                        }
                    ]
                })


        return filter_query

    @staticmethod
    def filter_resume(request):
        try:
            query_params = ResumeController.extract_query_params(request)
            filter_query = ResumeController.build_filter_query(query_params)
            print(filter_query)

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

            if request.query_params.get('format_type') == 'csv':
                return ResumeController.generate_csv_response(paginated_resumes)

            return paginator.get_paginated_response(paginated_resumes)

        except ValueError as e:
            logger.error(f"Error filtering resumes: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in filtering resumes: {str(e)}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def generate_csv_response(resumes):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="resumes.csv"'
        writer = csv.writer(response)
        
        headers = ['Name', 'Email', 'Mobile', 'City', 'Country', 'Title']

        headers += [f'Language{i+1}' for i in range(5)]
        headers += [f'Framework{i+1}' for i in range(5)]
        headers += [f'Technology{i+1}' for i in range(5)]
        
        headers += ['LLM Experience', 'Gen AI Experience'] + [f'Skill_Experience_{i+1}' for i in range(5)]
        
        for i in range(5):
            headers += [f'School_Name{i+1}', f'Degree_Name{i+1}', f'City{i+1}', f'Country{i+1}', 
                        f'Year_Of_Start{i+1}', f'Year_Of_Graduation{i+1}', f'Duration_In_Years{i+1}', 
                        f'Degree_Level{i+1}',f'Is Cs Degree{i+1}',f'Is ML Degree{i+1}',f'Institute Type{i+1}']

        for i in range(5):
            headers += [f'Company_Name{i+1}', f'Position_Held{i+1}', f'City{i+1}', f'Country{i+1}', 
                        f'Joining_Date{i+1}', f'Leaving_Date{i+1}', f'Total_Duration{i+1}',f'Company Size Range{i+1}',
                        f'Total Capital Raised{i+1}',f'Company Type{i+1}',f'Is Faang{i+1}',
                         f'has_the_company_raised_capital_in_the_last_5_years{i+1}',
                         f'Is Startup{i+1}']
        
        for i in range(5):
            headers += [f'Project_Name{i+1}', f'Project_Description{i+1}']

        headers += [
            'Last_Position_Held', 'Years_Of_Full_Time_Experience', 'Total_Startup_Experience', 
            'Total_Early_Stage_Startup_Experience', 'Product_Company_Experience', 
            'Service_Company_Experience', 'Gen_AI_Experience', 'Overall_Summary'
        ]
        headers.append('Parsed Data')

        writer.writerow(headers)
        
        for resume in resumes:
            row = []
            parsed_data = resume.get('parsed_data', {})

            personal_info = parsed_data.get('personal_information', {})
            row += [
                personal_info.get('name', ''),
                personal_info.get('email', ''),
                personal_info.get('mobile', ''),
                personal_info.get('city', ''),
                personal_info.get('country', ''),
                parsed_data.get('title', '')
            ]

            for skill_type in ['languages', 'frameworks', 'technologies']:
                skills = parsed_data.get('skills', {}).get(skill_type, {})
                proficient = skills.get('proficient', [])
                average = skills.get('average', [])
                combined = proficient[:5] + average[:5 - len(proficient)] 
                row += combined + [''] * (5 - len(combined))  

            total_skill_experience = parsed_data.get('skills', {}).get('total_skill_experience', {})
            top_5_skills = list(total_skill_experience.items())[:5]  
            row += [parsed_data.get('skills', {}).get('llm_experience', False),
                    parsed_data.get('skills', {}).get('gen_ai_experience', False)]
            row += [f'{skill}: {exp}' for skill, exp in top_5_skills] + [''] * (5 - len(top_5_skills))  

            educations = [parsed_data.get('education', {})]  
            educations = educations[:5] + [{}] * (5 - len(educations))  
            for edu in educations:
                row += [
                    edu.get('school_name', ''),
                    edu.get('degree_name', ''),
                    edu.get('city', ''),
                    edu.get('country', ''),
                    edu.get('year_of_start', ''),
                    edu.get('year_of_graduation', ''),
                    edu.get('duration_in_years', ''),
                    edu.get('degree_level', ''),
                    edu.get('is_cs_degree'),
                    edu.get('is_ml_degree'),
                    edu.get('institute_type')
                ]
                
            # BUG: the response in the parsed_data used this {},[{}] to make sub-fields of experience field
            # Parsed_data is received after filtering the get request means there is some issue in the given data from the gpt
            # As the gpt response is just converted into json in stored in the mongodb

            #print(parsed_data)
            experiences = parsed_data.get('experience', [])[:5]  
            experiences = experiences + [{}] * (5 - len(experiences))  
            for exp in experiences:
                company_info = exp.get('company_information', {})
                position = exp.get('positions_held_within_the_company', [{}])[0]
                row += [
                    company_info.get('name', ''),
                    position.get('position_name', ''),
                    company_info.get('city', ''),
                    company_info.get('country', ''),
                    company_info.get('joining_month_and_year', ''),
                    company_info.get('leaving_month_and_year', ''),
                    company_info.get('total_duration_in_years', ''),
                    company_info.get('company_size_range'),
                    company_info.get('total_capital_raised'),
                    company_info.get('company_type'),
                    company_info.get('is_fang'),
                    company_info.get('has_the_company_raised_capital_in_the_last_5_years?'),
                    company_info.get('is_startup')
                ]

            projects = parsed_data.get('projects_outside_of_work', [])[:5]  
            projects = projects + [{}] * (5 - len(projects)) 
            for project in projects:
                row += [
                    project.get('project_name', ''),
                    project.get('project_description', '')
                ]
            
            additional_experience = parsed_data.get('additional_experience_summary', {})
            row += [
                additional_experience.get('last_position_held', ''),
                additional_experience.get('years_of_full_time_experience_after_graduation', ''),
                additional_experience.get('total_startup_experience', ''),
                additional_experience.get('total_early_stage_startup_experience', ''),
                additional_experience.get('product_company_experience', ''),
                additional_experience.get('service_company_experience', ''),
                additional_experience.get('gen_ai_experience', '')
            ]

            row.append(parsed_data.get('overall_summary_of_candidate', ''))
            row.append(json.dumps(parsed_data))

            writer.writerow(row)

        return response


def split_and_strip(params, key):
        if key in params:
            return [tech.strip() for tech in params[key].split(',')]
        return []