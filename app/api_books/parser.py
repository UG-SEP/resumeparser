import requests
import json
import os
from resumeparser.settings import logger

def extract_info_from_resume(resume_text):
    prompt_str = """
    Extract the following information from the resume and provide it in a JSON format as specified below. If the candidate does not have a "Projects" section outside of work experience, eliminate the candidate from consideration.

    personal_information:
    - name
    - email
    - mobile
    - city (If not available then take the latest workplace)
    - country
    - linkdin
    - github

    resume_type: <type_of_engineer>

    title:
    - Provide a title for the candidate in the format: "<Type_of_Engineer> with <total_years_of_experience>". The role should be based on the candidate's overall experience and skills, such as:
    - backend_engineer
    - frontend_engineer
    - full_stack_engineer
    - devops_engineer
    - qa_engineer
    - test_engineer
    - ai_engineer
    - machine_learning_engineer
    - data_scientist
    - tech_lead
    - director
    - engineering_manager
    - ml_research_engineer
    - ml_ops_engineer
    - computer_vision_engineer
    - natural_language_processing_(NLP)_engineer
    - reinforcement_learning_engineer

    skills:
    - languages:
    - proficient:
        - List the first 2-3 languages the candidate is proficient in (e.g., Python, Java, JavaScript).
    - average:
        - List the remaining languages the candidate has average experience with.
    
    - frameworks:
    - proficient:
        - List the first 2-3 frameworks the candidate is proficient in (e.g., Django, Flask, React).
    - average:
        - List the remaining frameworks the candidate has average experience with.
    
    - technologies:
    - proficient:
        - List the first 2-3 technologies the candidate is proficient in (e.g., Docker, Kubernetes, AWS).
    - average:
        - List the remaining technologies the candidate has average experience with.
    
    - total_skill_experience (e.g., {"skill_name": "<int:number_of_years>"})
    - llm_experience (True/False)
    - gen_ai_experience (True/False, based on their projects or work experience)

    education:
    - school_name
    - degree_name
    - city
    - country
    - year_of_start
    - year_of_graduation
    - duration_in_years
    - mode (online/offline)
    - degree_level (bachelors/masters)
    - is_cs_degree (True/False)
    - is_ml_degree (True/False)
    - institute_type (IIT/IIIT/BITs/NIT/Other)

    experience:
    - company_information:
    - name
    - last_position_held
    - city
    - country
    - joining_month_and_year
    - leaving_month_and_year
    - total_duration_in_years
    - company_size_range (e.g., 1-50, 51-200, etc.)
    - total_capital_raised (Search it)
    - company_type (Product/Service)
    - is_faang (True/False)
    - has_the_company_raised_capital_in_the_last_5_years? (Yes/No)
    - is_startup (True/False based on whether the company has raised capital in the last 5 years)
    

    - positions_held_within_the_company:
    - position_name
    - position_starting_date
    - position_ending_date
    - projects:
        - Project_Name
        - Project_Description

    projects_outside_of_work (if available):
    - project_name
    - project_description

    additional_experience_summary:
    - last_position_held: <Last Position of the last company>
    - years_of_full_time_experience_after_graduation: <number_of_years>
    - total_startup_experience
    - total_early_stage_startup_experience (If company size is less than 50 then it is early stage startup)
    - product_company_experience (Total years of experience in product-based companies)
    - service_company_experience
    - gen_ai_experience (True/False, based on whether the candidate has any Gen AI projects in work or outside of work)

    achievements_awards:
    - summary_of_achievements_awards
    - position_blurbs (Position-wise short descriptions of achievements)

    overall_summary_of_candidate:
    - A short summary of the candidate's profile based on the provided information.
    """




    url = os.getenv("SERVER_URL")
    headers = {
        'Content-Type': 'application/json',
        'api-key': os.getenv('API_KEY')
    }

    payload = json.dumps({
        "messages": [
            {
                "role": "system",
                "content": prompt_str + "\n\n" + resume_text
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 3000
    })

    try:
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            json_data = response.json()
            response_content = json_data.get('choices', [{}])[0].get('message', {}).get('content', None)
            response_content = response_content.replace("```json", "").replace("```", "")
            try:
                parsed_data = json.loads(response_content)
                logger.info("Information extracted successfully.")
                return parsed_data
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON data: {e}")
                logger.info(f'Are you sure the response content contain valid json format?')
                return
                 
        else:
            logger.error(f"Error in API response: {response.status_code}")
            return None

    except requests.RequestException as e:
        logger.error(f"API request error: {e}", exc_info=True)
        return None
