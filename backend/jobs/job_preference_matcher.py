from typing import Dict, Any, List

class JobPreferenceMatcher:
    @staticmethod
    def evaluate_preference_match(
        job: Dict[str, Any],
        preferences: Dict[str, Any],
        resume_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluates a job against the candidate's career preferences and resume details,
        providing match percentages, explanations, and skill gap recommendations.
        """
        # Load user preference lists
        pref_roles = [r.strip().lower() for r in preferences.get("preferred_roles", [])] if isinstance(preferences.get("preferred_roles"), list) else [r.strip().lower() for r in preferences.get("preferred_roles", "").split(",") if r.strip()]
        pref_tech = [t.strip().lower() for t in preferences.get("preferred_technologies", [])] if isinstance(preferences.get("preferred_technologies"), list) else [t.strip().lower() for t in preferences.get("preferred_technologies", "").split(",") if t.strip()]
        pref_industries = [i.strip().lower() for i in preferences.get("preferred_industries", [])] if isinstance(preferences.get("preferred_industries"), list) else [i.strip().lower() for i in preferences.get("preferred_industries", "").split(",") if i.strip()]
        
        pref_level = preferences.get("experience_level", "").strip().lower()
        pref_remote = preferences.get("remote_preference", "").strip().lower()
        pref_location = preferences.get("location_preference", "").strip().lower()
        
        # Job variables
        job_title = job.get("title", job.get("job_title", "")).lower()
        job_desc = job.get("description", "").lower()
        job_category = job.get("category", "").lower()
        job_location = job.get("candidate_required_location", "").lower()
        
        # Match variables
        reasons = []
        score_boost = 0.0
        
        # 1. Role match
        role_matched = False
        for role in pref_roles:
            if role in job_title:
                reasons.append(f"Target role alignment: '{role.title()}' matches this position")
                score_boost += 15.0
                role_matched = True
                break
                
        # 2. Industry match
        industry_matched = False
        for ind in pref_industries:
            if ind in job_category or ind in job_title or ind in job_desc:
                reasons.append(f"Industry preference: Alignment with your '{ind.title()}' preference")
                score_boost += 10.0
                industry_matched = True
                break
                
        # 3. Technologies match
        matched_tech = []
        for tech in pref_tech:
            if tech in job_title or tech in job_desc:
                matched_tech.append(tech)
                
        if matched_tech:
            reasons.append(f"Preferred tech stack: Job requests {', '.join([t.title() for t in matched_tech[:3]])}")
            score_boost += min(15.0, len(matched_tech) * 5.0)
            
        # 4. Resume skills matches
        matched_resume_skills = []
        missing_skills = []
        # Extract keywords
        tech_keywords = ["python", "fastapi", "react", "next.js", "docker", "kubernetes", "aws", "gcp", "mongodb", "sql", "javascript", "typescript", "django", "nodejs", "git", "rest api"]
        job_skills = [tk for tk in tech_keywords if tk in job_title or tk in job_desc]
        
        lower_resume_skills = [s.lower() for s in resume_skills]
        for skill in job_skills:
            if skill in lower_resume_skills:
                matched_resume_skills.append(skill)
            else:
                missing_skills.append(skill)
                
        if matched_resume_skills:
            reasons.append(f"Matched because your resume contains {', '.join([s.upper() for s in matched_resume_skills[:3]])}")
            
        # 5. Remote and Location preferences
        is_remote_job = "remote" in job_title or "remote" in job_desc or "worldwide" in job_location or "anywhere" in job_location
        if pref_remote == "remote" and is_remote_job:
            reasons.append("Location preference: Remote job aligns with your remote preference")
            score_boost += 10.0
        elif pref_location and pref_location in job_location:
            reasons.append(f"Location preference: Job matches your target location '{pref_location.title()}'")
            score_boost += 10.0
            
        # Calculate match percentage
        base_match = 50.0
        if job_skills:
            skills_ratio = len(matched_resume_skills) / len(job_skills)
            base_match += (skills_ratio * 30.0)
        else:
            base_match += 20.0
            
        final_score = min(100, int(base_match + score_boost))
        
        # Build skill gaps and recommendations
        skill_gaps = []
        recommended_certs = []
        
        cert_map = {
            "kubernetes": "Certified Kubernetes Application Developer (CKAD)",
            "aws": "AWS Certified Developer Associate",
            "docker": "Docker Certified Associate",
            "gcp": "Google Cloud Professional Developer",
            "react": "Meta Front-End Developer Professional Certificate",
            "python": "PCEP – Certified Entry-Level Python Programmer"
        }
        
        for idx, skill in enumerate(missing_skills[:3]):
            impact = 12 - (idx * 2)
            skill_gaps.append({
                "skill": skill.title(),
                "impact": f"{impact}%"
            })
            if skill in cert_map:
                recommended_certs.append({
                    "skill": skill.title(),
                    "certification": cert_map[skill]
                })
                
        # Fallbacks
        if not skill_gaps:
            skill_gaps = [{"skill": "System Architecture", "impact": "8%"}]
        if not recommended_certs:
            recommended_certs = [{"skill": "Cloud Deployment", "certification": "AWS Certified Solutions Architect"}]
            
        return {
            "match_percentage": final_score,
            "match_reasons": reasons,
            "skill_gaps": skill_gaps,
            "recommended_certifications": recommended_certs
        }
