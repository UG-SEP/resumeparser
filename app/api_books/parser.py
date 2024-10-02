import os
import logging
from dotenv import load_dotenv
import openai
import json

load_dotenv()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_info_from_resume(resume_text):
    openai.api_key = os.environ.get("API_KEY")  
    prompt = f"""
    Please extract the following information from the resume. If any field is missing, return null for that field. For multiple work experiences, list each company separately in the 'Work Experience' array. Make sure to extract all information, including city and country, if present. The output should strictly follow the JSON structure provided below.

    1. Extract personal details, such as name, email, mobile number, LinkedIn, and Github.
    2. Extract all educational qualifications including college name, degree name, city, country, year of start, year of graduation, etc.
    3. Extract work experiences, including company name, position, city, country, dates of employment, and any other related fields.
    4. Extract skills, such as languages, frameworks, and technologies.
    5. Extract any awards or achievements mentioned.

    ### Expected JSON structure:
    {{
        "Date": null,
        "Personal Information": {{
            "Name": null,
            "Email": null,
            "Mobile": null,
            "Country": null,
            "City": null,
            "Resume Category": "(Frontend Developer/Backend Developer /Full Stack Developer/Android Developer/Data Scientist) Choose any one of the given choice by reviewing the work and skills",
            "LinkedIn": null,
            "Github": null
        }},
        "Skills": {{
            "Languages": null,
            "Frameworks": null,
            "Technologies": null
        }},
        "Education": {{
            "College Name": null,
            "Degree Name": null,
            "Country": null,
            "City": null,
            "Year of Start": null,
            "Year of Graduation": null,
            "Duration in Years": null,
            "Mode": null,
            "Degree Type": "(Bachelor/Master)",
            "CS Degree": "(Yes/No)",
            "ML Degree": "(Yes/No)",
            "IIT/NIT/IIIT/BIT": "(Yes/No)"
        }},
        "Work Experience": [
            {{
                "Company Name": null,
                "Position Name": null,
                "City": null,
                "Country": null,
                "Joining Date": null,
                "Leaving Date": null,
                "Total Duration": null,
                "Company Size Range": null,
                "Total Capital Raised": null,
                "Company Type": null,
                "FAANG": "(Yes/No)",
                "Startup Experience": null,
                "Experience with LLM": null
            }}
        ],
        "Achievements": {{
            "Other Achievements/Awards": null,
            "Summary of Achievements": null
        }}
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
        response_content = response_content.replace("},", "},")
        response_content = response_content.replace("}},", "}},")
        
        json_data = json.loads(response_content)
        logger.info("Information extracted successfully.")
        return json_data

    except (KeyError, json.JSONDecodeError) as e:
        logger.error(f"Error extracting information: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None
