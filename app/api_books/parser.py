import os
from resumeparser.settings import logger
from dotenv import load_dotenv
import openai
import json

load_dotenv()


def extract_info_from_resume(resume_text):
    openai.api_key = os.environ.get("API_KEY")  
    prompt = f"""
    Please extract the following information from the resume. If any field is missing, return null or an empty string as per the structure. For multiple work experiences, list each company separately in the 'experience.company' array. Make sure to extract all relevant information, including city, country, and job details if present. The output should strictly follow the JSON structure provided below.

    1. Extract personal information, such as name, email, mobile, LinkedIn, and Github.
    2. Extract all educational qualifications, including school name, degree name, city, country, year of start, year of graduation, etc.
    3. Extract work experiences, including company name, position, city, country, dates of employment, project descriptions, achievements, etc.
    4. Extract skills, such as languages, frameworks, technologies, and experience related to LLM and Gen-AI.
    5. Extract achievements or awards mentioned.

    ### Expected JSON structure:
    {{
      "personal_information": {{
        "name": "",
        "email": "",
        "mobile": "",
        "city": "",
        "country": "",
        "linkedin": "",
        "github": ""
      }},
      "skills": {{
        "languages": [],
        "frameworks": [],
        "technologies": [],
        "total_skill_experience": {{"skill_name":"no_of_years"}},
        "llm_experience": false,
        "gen_ai_experience": false
      }},
      "education": [
        {{
          "school_name": "",
          "degree_name": "",
          "city": "",
          "country": "",
          "year_of_start": "",
          "year_of_graduation": "",
          "duration_in_years": "",
          "mode": "online/offline",
          "degree_level": "bachelors/masters",
          "is_cs_degree": false,
          "is_ml_degree": false,
          "institute_type": "IIT/IIIT/BITs/NIT/Other"
        }}
      ],
      "experience": {{
        "company": [{{
          "name": "company-1",
          "last_position": "",
          "city": "",
          "country": "",
          "joining_month_year": "",
          "leaving_month_year": "",
          "total_duration_in_years": "",
          "size_range": "",
          "total_capital_raised": "",
          "company_type": "Product/Service",
          "is_faang": false,
          "positions": [
            {{
              "name": "position1",
              "position_starting_date": "",
              "position_ending_date": "",
              "projects": {{"name": "", "description": ""}},
              "achievements": []
            }}
          ]
        }}],
        "total_experience": "",
        "total_startup_experience": "",
        "total_early_stage_startup_experience": "",
        "product_company_experience": "",
        "service_company_experience": ""
      }},
      "achievements_awards": {{
        "summary": "",
        "position_blurbs": [
          {{
            "position": "",
            "blurb": ""
          }}
        ]
      }},
      "resume_type": "Backend/FE/Fullstack/Devops/QA/Test/AI/Tech Lead/Director/Engineering Manager/Data Scientist/Data Analyst",
      "overall_summary_of_candidate": ""
    }}

    Resume Text:
    {resume_text}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant extracting structured data from resumes."},
                {"role": "user", "content": prompt}
            ]
        )

        response_content = response.get('choices', [{}])[0].get('message', {}).get('content', None)
        response_content = response_content.replace("```json", "").replace("```", "")
        
        json_data = json.loads(response_content)
        logger.info("Information extracted successfully.")
        return json_data

    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error extracting information: {e}",exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}",exc_info=True)
        return None
