import re
from datetime import datetime
from typing import List, Dict, Any

from jobs.skill_matcher import SkillMatcher
from jobs.semantic_matcher import SemanticMatcher

class ScoringEngine:
    CURRENT_YEAR = 2026

    @classmethod
    def parse_experience_years(cls, experience: List[Dict[str, Any]]) -> float:
        """
        Parses years of experience from experience duration strings using heuristics.
        """
        if not experience:
            return 0.0

        total_years = 0.0
        year_pattern = r'\b(19\d{2}|20[0-2]\d)\b'

        for exp in experience:
            duration = exp.get("duration", "")
            if not duration:
                # Add default heuristic per job entry if duration is missing
                total_years += 1.5
                continue

            years = [int(y) for y in re.findall(year_pattern, duration)]
            if len(years) == 2:
                diff = abs(years[1] - years[0])
                total_years += max(0.5, float(diff))
            elif len(years) == 1:
                # E.g. "2022 - Present"
                if "present" in duration.lower() or "current" in duration.lower():
                    diff = abs(cls.CURRENT_YEAR - years[0])
                    total_years += max(0.5, float(diff))
                else:
                    total_years += 1.0
            else:
                total_years += 1.5

        return round(total_years, 1)

    @classmethod
    def evaluate_job_match(
        cls, 
        resume_data: Dict[str, Any], 
        job_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates compatibility score between a resume and a job role.
        
        Weights:
            - Skills Match (required vs possessed): 40%
            - Experience Match (level + years): 25%
            - Project Alignment (semantic text overlap): 20%
            - Education & ATS base score: 10%
            - Certifications Match: 5%
        """
        # 1. Skills Matching (40%)
        user_skills = resume_data.get("skills", [])
        req_skills = job_details.get("required_skills", [])
        skill_res = SkillMatcher.match_skills(user_skills, req_skills)
        skills_score = skill_res["match_ratio"] # 0 to 100

        # 2. Experience Level Matching (25%)
        exp_years = cls.parse_experience_years(resume_data.get("experience", []))
        req_years = job_details.get("experience_years_required", 2)
        req_level = job_details.get("experience_level", "Intermediate").lower()

        if req_level == "junior":
            exp_level_score = 100.0 if exp_years >= req_years else (exp_years / max(1, req_years)) * 100.0
        elif req_level == "senior":
            target = max(5, req_years)
            exp_level_score = 100.0 if exp_years >= target else (exp_years / target) * 100.0
        else: # Intermediate
            target = max(3, req_years)
            exp_level_score = 100.0 if exp_years >= target else (exp_years / target) * 100.0

        # Normalize score bounds
        exp_score = min(100.0, max(0.0, exp_level_score))

        # 3. Project & Text Description Alignment (20%)
        semantic_res = SemanticMatcher.match_projects_and_experience(
            projects=resume_data.get("projects", []),
            experience=resume_data.get("experience", []),
            job_details=job_details
        )
        project_score = semantic_res["overall_semantic_score"]

        # 4. Education & Base ATS Quality (10%)
        # Degree check
        edu_list = resume_data.get("education", [])
        degree_match = False
        degree_keywords = ["bachelor", "master", "ph.d", "btech", "mtech", "degree", "bs", "ms", "computer", "engineering"]
        for edu in edu_list:
            degree_str = f"{edu.get('degree', '')} {edu.get('institution', '')}".lower()
            if any(kw in degree_str for kw in degree_keywords):
                degree_match = True
                break
        
        edu_score = 100.0 if degree_match else 50.0
        ats_base = float(resume_data.get("ats_score", 70))
        education_score = (edu_score * 0.4) + (ats_base * 0.6)

        # 5. Certifications (5%)
        certs = resume_data.get("certifications", [])
        # Give partial credit if user has certifications, full if matched
        certs_score = 100.0 if len(certs) >= 2 else (50.0 if len(certs) == 1 else 0.0)

        # Weighted calculation
        total_score = (
            (skills_score * 0.40) +
            (exp_score * 0.25) +
            (project_score * 0.20) +
            (education_score * 0.10) +
            (certs_score * 0.05)
        )
        total_score = round(min(100.0, max(0.0, total_score)), 1)

        # Job readiness badge designation
        if total_score >= 85:
            readiness = "Excellent Fit"
        elif total_score >= 70:
            readiness = "Strong Alignment"
        elif total_score >= 50:
            readiness = "Potential Fit"
        else:
            readiness = "Needs Upskilling"

        return {
            "job_title": job_details["job_title"],
            "match_percentage": int(total_score),
            "readiness_level": readiness,
            "skills_score": int(skills_score),
            "experience_score": int(exp_score),
            "project_score": int(project_score),
            "education_score": int(education_score),
            "certs_score": int(certs_score),
            "matching_skills": skill_res["matching_skills"],
            "missing_skills": skill_res["missing_skills"],
            "extra_skills": skill_res["extra_skills"],
            "candidate_exp_years": exp_years,
            "required_exp_years": req_years
        }
