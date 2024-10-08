import requests
import json
import os
from resumeparser.settings import logger

def extract_info_from_resume(resume_text):
    # prompt_str = f"""
    # Please extract the following information from the resume. If any field is missing, return null or an empty string as per the structure. For multiple work experiences, list each company separately in the 'experience.company' array. Make sure to extract all relevant information, including city, country, and job details if present. The output should strictly follow the JSON structure provided below.

    # 1. Extract personal information, such as name, email, mobile, LinkedIn, and Github.
    # 2. Extract all educational qualifications, including school name, degree name, city, country, year of start, year of graduation, etc.
    # 3. Extract work experiences, including company name, position, city, country, dates of employment, project descriptions, achievements, etc.
    # 4. Extract skills, such as languages, frameworks, technologies, and experience related to LLM and Gen-AI.
    # 5. Extract achievements or awards mentioned.

    # ### Expected JSON structure:
    # {{
    #   "personal_information": {{
    #     "name": "",
    #     "email": "",
    #     "mobile": "",
    #     "city": "",
    #     "country": "",
    #     "linkedin": "",
    #     "github": ""
    #   }},
    #   "skills": {{
    #     "languages": [],
    #     "frameworks": [],
    #     "technologies": [],
    #     "total_skill_experience": {{"skill_name":"no_of_years"}},
    #     "llm_experience": false,
    #     "gen_ai_experience": false
    #   }},
    #   "education": [
    #     {{
    #       "school_name": "",
    #       "degree_name": "",
    #       "city": "",
    #       "country": "",
    #       "year_of_start": "",
    #       "year_of_graduation": "",
    #       "duration_in_years": "",
    #       "mode": "online/offline",
    #       "degree_level": "bachelors/masters",
    #       "is_cs_degree": false,
    #       "is_ml_degree": false,
    #       "institute_type": "IIT/IIIT/BITs/NIT/Other"
    #     }}
    #   ],
    #   "experience": {{
    #     "company": [{{
    #       "name": "company-1",
    #       "last_position": "",
    #       "city": "",
    #       "country": "",
    #       "joining_month_year": "",
    #       "leaving_month_year": "",
    #       "total_duration_in_years": "",
    #       "size_range": "",
    #       "total_capital_raised": "",
    #       "company_type": "Product/Service",
    #       "is_faang": false,
    #       "positions": [
    #         {{
    #           "name": "position1",
    #           "position_starting_date": "",
    #           "position_ending_date": "",
    #           "projects": {{"name": "", "description": ""}},
    #           "achievements": []
    #         }}
    #       ]
    #     }}],
    #     "total_experience": "",
    #     "total_startup_experience": "",
    #     "total_early_stage_startup_experience": "",
    #     "product_company_experience": "",
    #     "service_company_experience": ""
    #   }},
    #   "achievements_awards": {{
    #     "summary": "",
    #     "position_blurbs": [
    #       {{
    #         "position": "",
    #         "blurb": ""
    #       }}
    #     ]
    #   }},
    #   "resume_type": "Backend/FE/Fullstack/Devops/QA/Test/AI/Tech Lead/Director/Engineering Manager/Data Scientist/Data Analyst",
    #   "overall_summary_of_candidate": ""
    # }}
    # """

    # url = os.getenv("SERVER_URL")
    # headers = {
    #     'Content-Type': 'application/json',
    #     'api-key': os.getenv('API_KEY')
    # }

    # payload = json.dumps({
    #     "messages": [
    #         {
    #             "role": "system",
    #             "content": prompt_str + "\n\n" + resume_text
    #         }
    #     ],
    #     "temperature": 0.7,
    #     "top_p": 0.95,
    #     "max_tokens": 1500
    # })

    # try:
    #     response = requests.post(url, headers=headers, data=payload)

    #     if response.status_code == 200:
    #         # Convert the response to JSON
    #         json_data = response.json()

    #         # Now safely access keys within the JSON data
    #         response_content = json_data.get('choices', [{}])[0].get('message', {}).get('content', None)

    #         # Clean up response_content if needed
    #         response_content = response_content.replace("```json", "").replace("```", "")

    #         # Parse response_content as a dictionary
    #         logger.info(f"Raw API Response: {response_content}")

    #         parsed_data = json.loads(response_content)
            
    #         logger.info("Information extracted successfully.")
    #         return parsed_data  # Return the parsed dictionary instead of the raw string
    #     else:
    #         logger.error(f"Error in API response: {response.status_code}")
    #         return None

    # except requests.RequestException as e:
    #     logger.error(f"API request error: {e}", exc_info=True)
    #     return None
    data ="""
 {
    "Personal Information": {
        "Name": "Devansh Sood",
        "Email": "demo@gmail.com",
        "Mobile": "+91 1234567890",
        "City": "Gurgaon",
        "Country": "India",
        "LinkedIn": null,
        "GitHub": null
    },
    "Skills": {
        "Languages": [
            "Python",
            "Shell Scripting"
        ],
        "Frameworks": [
            "Django",
            "Flask",
            "FastAPI",
            "React.js"
        ],
        "Technologies": [
            "MySQL",
            "MongoDB",
            "Kafka"
        ],
        "Total Skill Experience": {
            "Python": "5+ years",
            "Django": "5+ years",
            "Flask": "5+ years",
            "FastAPI": "5+ years",
            "React.js": "5+ years",
            "Shell Scripting": "5+ years"
        },
        "LLM Experience": false,
        "Gen AI Experience": true
    },
    "Education": {
        "School Name": "Manipal University Jaipur",
        "Degree Name": "B.Tech: Computer Science and Engineering",
        "City": "Jaipur",
        "Country": "India",
        "Year of Start": 2015,
        "Year of Graduation": 2019,
        "Duration in Years": 4,
        "Mode": "offline",
        "Degree Level": "bachelors",
        "Is CS Degree": true,
        "Is ML Degree": false,
        "Institute Type": "Other"
    },
    "Experience": [
        {
            "Company Information": {
                "Name": "Leegality",
                "Last Position Held": "Senior Software Developer",
                "City": "Gurgaon",
                "Country": "India",
                "Joining Month and Year": "08/2021",
                "Leaving Month and Year": "05/2024",
                "Total Duration in Years": 2.75,
                "Company Size Range": "51-200",
                "Total Capital Raised": null,
                "Company Type": "Product",
                "Is FAANG": false
            },
            "Positions Held within the Company": [
                {
                    "Position Name": "Senior Software Developer",
                    "Position Starting Date": "07/2022",
                    "Position Ending Date": "05/2024",
                    "Projects": [
                        {
                            "Project Name": "Deal Collab",
                            "Project Description": "Led a team in the creation of templates with an integrated document editor, streamlining the contract drafting process."
                        },
                        {
                            "Project Name": "Face Match",
                            "Project Description": "Worked on the development of a face matching machine learning project, integrating advanced technologies for facial recognition, similarity analysis, and liveliness detection."
                        },
                        {
                            "Project Name": "Smart Name Verification",
                            "Project Description": "Worked on machine learning based projects specializing in identifying the similarity between two names."
                        }
                    ],
                    "Achievements": [
                        "Consolidated multiple functionalities into a single platform, eliminating the need for separate tools for drafting, editing, negotiation, search, storage, analytics, and e-signature.",
                        "Achieved a remarkable 94% accuracy rate in identifying name similarity, surpassing the industry standard.",
                        "Significantly reduced the false prediction rate from 85%, by implementing advanced machine learning models."
                    ]
                },
                {
                    "Position Name": "Software Developer",
                    "Position Starting Date": "08/2021",
                    "Position Ending Date": "07/2022",
                    "Projects": [
                        {
                            "Project Name": "Stamp Panel",
                            "Project Description": "Created a microservice for the stamp panel dashboard which helps various employees to process and deliver digital stamp papers to vendors."
                        }
                    ],
                    "Achievements": [
                        "The project was beneficial for the firm. It has reduced working time and manpower by 60%.",
                        "Removed the frequent follow-ups from other teams."
                    ]
                }
            ]
        },
        {
            "Company Information": {
                "Name": "Quadeye Securities LLP",
                "Last Position Held": "Software Developer",
                "City": "Gurgaon",
                "Country": "India",
                "Joining Month and Year": "05/2020",
                "Leaving Month and Year": "07/2021",
                "Total Duration in Years": 1.2,
                "Company Size Range": "51-200",
                "Total Capital Raised": null,
                "Company Type": "Product",
                "Is FAANG": false
            },
            "Positions Held within the Company": [
                {
                    "Position Name": "Software Developer",
                    "Position Starting Date": "05/2020",
                    "Position Ending Date": "07/2021",
                    "Projects": [
                        {
                            "Project Name": "Strategy Error Dashboard",
                            "Project Description": "Created a dashboard using Django and React which helps the strategy monitor to view and handle all the errors of running strategy from a single platform."
                        },
                        {
                            "Project Name": "Automation and Optimization of Recon Scripts",
                            "Project Description": "Worked on a project in order to keep the track of daily selling and buying of stocks."
                        }
                    ],
                    "Achievements": [
                        "Before the dashboard, the on-duty monitor had to check multiple Slack channels to check for errors, resulting in 3 out of 10 errors getting unnoticed. With the help of this dashboard, the frequency was reduced to 1 out of 20.",
                        "Successfully automated recon for 3 regions. Reduced the running time of pre-built scripts by 35 to 40%."
                    ]
                }
            ]
        },
        {
            "Company Information": {
                "Name": "Nineleaps Technology Solutions Pvt Ltd",
                "Last Position Held": "Software Developer",
                "City": "Bangalore",
                "Country": "India",
                "Joining Month and Year": "01/2019",
                "Leaving Month and Year": "05/2020",
                "Total Duration in Years": 1.33,
                "Company Size Range": "51-200",
                "Total Capital Raised": null,
                "Company Type": "Service",
                "Is FAANG": false
            },
            "Positions Held within the Company": [
                {
                    "Position Name": "Software Developer",
                    "Position Starting Date": "01/2019",
                    "Position Ending Date": "05/2020",
                    "Projects": [
                        {
                            "Project Name": "Long Range Forecast",
                            "Project Description": "Coded in Python and Spark to predict future sales and corresponding store demand for a particular product according to given client logic."
                        },
                        {
                            "Project Name": "Store Demand Forecast",
                            "Project Description": "Worked on a continuation of the Long Range Forecast in which we predicted the stock required for each item dynamically in each store according to previous sales and discounts data."
                        }
                    ],
                    "Achievements": [
                        "Successfully reduced the running time of store demand prediction by 50%."
                    ]
                }
            ]
        }
    ],
    "Achievements/Awards": [],
    "Resume Type": "Backend Developer",
    "Overall Summary of Candidate": "Experienced backend developer with 5+ years of experience specializing in Python, Django, Flask, and FastAPI. Proven track record of leading teams and delivering impactful solutions in various domains, including contract management, machine learning, and financial services.",
    "total_experience":"5",
    "total_startup_experience":"2",
    "total_early_stage_startup_experience":"1",
    "product_company_experience":"2",
    "service_company_experience":"3"

}
    """
    return json.loads(data)
     
