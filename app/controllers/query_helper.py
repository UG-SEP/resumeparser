def full_time_experience_query(params,filter_query):
    if params.get('full_time_experience'):
        filter_query["parsed_data.additional_experience_summary.years_of_full_time_experience_after_graduation"] =  {
                "$gte": int(params['full_time_experience'])
                }

def skills_experience_query(params,filter_query):
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

def company_type_query(params,filter_query):
    if params.get('company_type') == 'product':
        filter_query["parsed_data.additional_experience_summary.product_company_experience"] = {
            "$gt": 0
        }

def product_company_experience_query(params,filter_query):
    if params.get('product_company_experience'):
        filter_query["parsed_data.additional_experience_summary.product_company_experience"] = {
            "$gte": int(params['product_company_experience'])
        }

def startup_experience_query(params,filter_query):
    if params.get('startup_experience'):
        filter_query["parsed_data.additional_experience_summary.total_startup_experience"] = {
            "$gte": int(params['startup_experience'])
        }

def degree_type_query(params,filter_query):
    if params.get('degree_type'):
        filter_query["parsed_data.education.degree_level"] = {
            "$regex": f"^{params['degree_type']}$", "$options": "i"
        }

def last_position_held_query(params,filter_query):
    if params.get('last_position_held'):
        filter_query["parsed_data.additional_experience_summary.last_position_held"] = {
            "$regex": f".*{re.escape(params['last_position_held'])}.*",
            "$options": "i"
        }
        
def gen_ai_experience_query(params,filter_query):
     if params.get('gen_ai_experience'):
        filter_query["parsed_data.skills.gen_ai_experience"] = params['gen_ai_experience'].lower() == 'true'

def is_ml_degree_query(params,filter_query):
    if params.get('is_ml_degree'):
        filter_query["parsed_data.education.is_ml_degree"] = params['is_ml_degree'].lower() == 'true'

def is_cs_degree_query(params,filter_query):
    if params.get('is_cs_degree'):
        filter_query["parsed_data.education.is_cs_degree"] = params['is_cs_degree'].lower() == 'true'

def early_stage_startup_experience_query(params,filter_query):
    if params.get('early_stage_startup_experience'):
        filter_query["parsed_data.additional_experience_summary.total_early_stage_startup_experience"] = {
            "$gte": int(params['early_stage_startup_experience'])
        }

def institute_type_query(params,filter_query):
    if params.get('institute_type'):
        filter_query["parsed_data.education.institute_type"] = {
        "$regex": f"^{re.escape(params['institute_type'])}$",
        "$options": "i"  
    }

def llm_experience_query(params,filter_query):
    if params.get('llm_experience'):
        filter_query["parsed_data.skills.llm_experience"] = params['llm_experience'].lower() == 'true'

def service_company_experience_query(params,filter_query):
    if params.get('service_company_experience'):
        filter_query["parsed_data.additional_experience_summary.service_company_experience"] = {
            "$gte": int(params['service_company_experience'])
        }

def resume_type_query(params,filter_query):
    if params.get('resume_type'):
        filter_query["parsed_data.resume_type"] = {
            "$regex": f"^{params['resume_type']}$", "$options": "i"
        }

def projects_outside_of_work_query(params,filter_query):
    if params.get('projects_outside_of_work'):
        filter_query["parsed_data.projects_outside_of_work"] = {"$exists": True, "$ne": []}

def skills_query(params,filter_query):
    if params.get('skills'):
        skills = split_and_strip(params,'skills')
        if skills:
            pattern = '|'.join(map(re.escape, skills))
            filter_query = {
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
            }

def proficient_technologies_query(params,filter_query):
    if params.get('proficient_technologies'):
        proficient_technologies = split_and_strip(params, 'proficient_technologies')
        if proficient_technologies:
            pattern = '|'.join(map(re.escape, proficient_technologies))

            filter_query = {
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
            }