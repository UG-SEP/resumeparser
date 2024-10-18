import re
from datetime import datetime, timedelta
from app.models import Resume
from django.utils import timezone
from bson import ObjectId

def full_time_experience_query(params,filter_query):
    if params.get('full_time_experience'):
        filter_query["parsed_data.additional_experience_summary.years_of_full_time_experience_after_graduation"] =  {
                "$gte": float(params['full_time_experience'])
                }

def skills_experience_query(params,filter_query):
    if params.get('skills_experience'):
        skills = split_and_strip(params, "skills_experience")

        skill_queries = []
        for skill in skills:
            skill_name, experience_years = skill.split('|')
            experience_years = float(experience_years)
            skill_query = {
                f"parsed_data.skills.total_skill_experience.{skill_name.lower()}": {
                    "$gte": experience_years
                }
            }
            skill_queries.append(skill_query)

        if skill_queries:
            if "$and" in filter_query:
                filter_query["$and"].append(skill_queries)
            else:
                filter_query["$and"] = skill_queries

def company_type_query(params,filter_query):
    if params.get('company_type') == 'product':
        filter_query["parsed_data.additional_experience_summary.product_company_experience"] = {
            "$gt": 0
        }

def product_company_experience_query(params,filter_query):
    if params.get('product_company_experience'):
        filter_query["parsed_data.additional_experience_summary.product_company_experience"] = {
            "$gte": float(params['product_company_experience'])
        }

def startup_experience_query(params,filter_query):
    if params.get('startup_experience'):
        filter_query["parsed_data.additional_experience_summary.total_startup_experience"] = {
            "$gte": float(params['startup_experience'])
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
            "$gte": float(params['early_stage_startup_experience'])
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
            "$gte": float(params['service_company_experience'])
        }

def resume_type_query(params,filter_query):
    if params.get('resume_type'):
        filter_query["parsed_data.resume_type"] = {
            "$regex": f"^{params['resume_type']}$", "$options": "i"
        }

def projects_outside_of_work_query(params,filter_query):
    if params.get('projects_outside_of_work'):
        filter_query["parsed_data.projects_outside_of_work"] = {"$exists": True, "$ne": []}

def skills_and_query(params, filter_query):
    if params.get('skills_and'):
        skills = split_and_strip(params, 'skills_and')
        if skills:
            skill_conditions = []

            for skill in skills:
                skill_conditions.append({
                    "$or": [
                       
                        {"parsed_data.skills.technologies.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.languages.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.frameworks.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.frameworks.average": {"$in": [skill]}},
                        {"parsed_data.skills.languages.average": {"$in": [skill]}},
                        {"parsed_data.skills.technologies.average": {"$in": [skill]}}
                    ]
                })

            if skill_conditions:
                if "$and" in filter_query:
                    filter_query["$and"].extend(skill_conditions)
                else:
                    filter_query["$and"] = skill_conditions

    return filter_query



def proficient_technologies_and_query(params,filter_query):
    if params.get('proficient_technologies_and'):
        proficient_technologies_and = split_and_strip(params, 'proficient_technologies_and')
        if proficient_technologies_and:
            proficient_technologies_condition = []
            for proficient_technology in proficient_technologies_and:
                proficient_technologies_condition.append({
                    "$or": [
                       
                        {"parsed_data.skills.technologies.proficient": {"$in": [proficient_technology]}},
                        {"parsed_data.skills.languages.proficient": {"$in": [proficient_technology]}},
                        {"parsed_data.skills.frameworks.proficient": {"$in": [proficient_technology]}},
                    ]
                })
            if proficient_technologies_condition:
                if "$and" in filter_query:
                    filter_query["$and"].extend(proficient_technologies_condition)
                else:
                    filter_query["$and"] = proficient_technologies_condition

    return filter_query


def skills_or_query(params, filter_query):
    if params.get('skills_or'):
        skills = split_and_strip(params, 'skills_or')
        if skills:
            skill_conditions = []

            for skill in skills:
                skill_conditions.append({
                    "$or": [
                       
                        {"parsed_data.skills.technologies.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.languages.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.frameworks.proficient": {"$in": [skill]}},
                        {"parsed_data.skills.frameworks.average": {"$in": [skill]}},
                        {"parsed_data.skills.languages.average": {"$in": [skill]}},
                        {"parsed_data.skills.technologies.average": {"$in": [skill]}}
                    ]
                })

            if skill_conditions:
                if "$or" in filter_query:
                    filter_query["$or"].extend(skill_conditions)
                else:
                    filter_query["$or"] = skill_conditions

    return filter_query



def proficient_technologies_or_query(params,filter_query):
    if params.get('proficient_technologies_or'):
        proficient_technologies_or = split_and_strip(params, 'proficient_technologies_or')
        if proficient_technologies_or:
            proficient_technologies_condition = []
            for proficient_technology in proficient_technologies_or:
                proficient_technologies_condition.append({
                    "$or": [
                       
                        {"parsed_data.skills.technologies.proficient": {"$in": [proficient_technology]}},
                        {"parsed_data.skills.languages.proficient": {"$in": [proficient_technology]}},
                        {"parsed_data.skills.frameworks.proficient": {"$in": [proficient_technology]}},
                    ]
                })
            if proficient_technologies_condition:
                if "$or" in filter_query:
                    filter_query["$or"].extend(proficient_technologies_condition)
                else:
                    filter_query["$or"] = proficient_technologies_condition

    return filter_query
            
def one_hour_filter(params, filter_query):
    time_threshold = timezone.now() - timedelta(hours=1)
    resumes = Resume.objects.filter(modified_at__gte=time_threshold) 
    parsed_data_ids = [resume.parsed_data_id for resume in resumes]
    filter_query["_id"] = {"$in": [ObjectId(id) for id in parsed_data_ids]}

def six_hour_filter(params, filter_query):
    time_threshold = timezone.now() - timedelta(hours=6)
    resumes = Resume.objects.filter(modified_at__gte=time_threshold)
    parsed_data_ids = [resume.parsed_data_id for resume in resumes]
    filter_query["_id"] = {"$in": [ObjectId(id) for id in parsed_data_ids]}

def twelve_hour_filter(params, filter_query):
    time_threshold = timezone.now() - timedelta(hours=12)
    resumes = Resume.objects.filter(modified_at__gte=time_threshold)
    parsed_data_ids = [resume.parsed_data_id for resume in resumes]
    filter_query["_id"] = {"$in": [ObjectId(id) for id in parsed_data_ids]}

def one_day_filter(params, filter_query):
    time_threshold = timezone.now() - timedelta(days=1)
    resumes = Resume.objects.filter(modified_at__gte=time_threshold)
    parsed_data_ids = [resume.parsed_data_id for resume in resumes]
    filter_query["_id"] = {"$in": [ObjectId(id) for id in parsed_data_ids]}

def seven_day_filter(params, filter_query):
    time_threshold = timezone.now() - timedelta(days=7)
    resumes = Resume.objects.filter(modified_at__gte=time_threshold)
    parsed_data_ids = [resume.parsed_data_id for resume in resumes]
    filter_query["_id"] = {"$in": [ObjectId(id) for id in parsed_data_ids]}



def split_and_strip(params, key):
        if key in params:
            return [tech.strip() for tech in params[key].split(',')]
        return []
