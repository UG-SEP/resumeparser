import requests
import json
import os
from resumeparser.settings import logger

def extract_info_from_resume(resume_text):
    prompt_str = """
    Extract the following information from the resume and provide it in a JSON format as specified below:

    Personal Information:
    •⁠  ⁠Name
    •⁠  ⁠Email
    •⁠  ⁠Mobile
    •⁠  ⁠City
    •⁠  ⁠Country
    •⁠  ⁠LinkedIn
    •⁠  ⁠GitHub

    Skills:
    •⁠  ⁠Languages
    •⁠  ⁠Frameworks
    •⁠  ⁠Technologies
    •⁠  ⁠Total Skill Experience (e.g., {"skill_name": "number_of_years"})
    •⁠  ⁠LLM Experience (True/False)
    •⁠  ⁠Gen AI Experience (True/False)

    Education:
    •⁠  ⁠School Name
    •⁠  ⁠Degree Name
    •⁠  ⁠City
    •⁠  ⁠Country
    •⁠  ⁠Year of Start
    •⁠  ⁠Year of Graduation
    •⁠  ⁠Duration in Years
    •⁠  ⁠Mode (online/offline)
    •⁠  ⁠Degree Level (bachelors/masters)
    •⁠  ⁠Is CS Degree (True/False)
    •⁠  ⁠Is ML Degree (True/False)
    •⁠  ⁠Institute Type (IIT/IIIT/BITs/NIT/Other)

    Experience:
    •⁠  ⁠Company Information:
      - Name
      - Last Position Held
      - City
      - Country
      - Joining Month and Year
      - Leaving Month and Year
      - Total Duration in Years
      - Company Size Range (e.g., 1-50, 51-200, etc.)
      - Total Capital Raised (if available)
      - Company Type (Product/Service)
      - Is FAANG (True/False)
    •⁠  ⁠Positions Held within the Company:
      - Position Name
      - Position Starting Date
      - Position Ending Date
      - Projects:
        - Project Name
        - Project Description
      - Achievements (List of specific achievements)

    Additional Experience Summary:
    •⁠  ⁠Total Experience
    •⁠  ⁠Total Startup Experience
    •⁠  ⁠Total Early Stage Startup Experience
    •⁠  ⁠Product Company Experience
    •⁠  ⁠Service Company Experience

    Achievements/Awards:
    •⁠  ⁠Summary of Achievements/Awards
    •⁠  ⁠Position Blurbs (Position-wise short descriptions of achievements)

    Resume Type:
    •⁠  ⁠Example: Data Scientist, Backend Developer, Fullstack Developer, AI Specialist, etc.

    Overall Summary of Candidate:
    •⁠  ⁠A short summary of the candidate's profile based on the provided information.
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
        "max_tokens": 1500
    })

    try:
        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            json_data = response.json()
            logger.info("Information extracted successfully.")
            return json_data
        else:
            logger.error(f"Error in API response: {response.status_code}")
            return None

    except requests.RequestException as e:
        logger.error(f"API request error: {e}", exc_info=True)
        return None
