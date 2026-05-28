from typing import Dict, Any
from bson import ObjectId
from database.mongodb import resumes_collection, users_collection
from nlp.semantic_resume_graph import SemanticResumeGraph

class ResumeContextEngine:
    @classmethod
    def get_unified_context(cls, resume_id: str, user_email: str) -> Dict[str, Any]:
        """
        Assembles the complete Unified Resume Intelligence Object by gathering 
        resume details, parser outputs, and user preferences from MongoDB.
        """
        if resumes_collection is None:
            return {}
            
        try:
            resume = resumes_collection.find_one({
                "_id": ObjectId(resume_id),
                "user_email": user_email
            })
        except Exception:
            return {}
            
        if not resume:
            return {}
            
        # Fetch user preferences
        career_preferences = {}
        if users_collection is not None:
            user = users_collection.find_one({"email": user_email})
            if user:
                career_preferences = user.get("career_preferences", {})
                
        # Build skills, frameworks, achievements list
        skills = resume.get("skills", [])
        projects = resume.get("projects", [])
        experience = resume.get("experience", [])
        ats_score = resume.get("ats_score", 0)
        
        # Determine ATS Weaknesses
        ats_weaknesses = resume.get("missing_skills", [])
        if not ats_weaknesses:
            ats_weaknesses = ["System Architecture", "Performance Optimization", "Automated Testing"]
            
        # Calculate dynamic recruiter score
        recruiter_score = int(ats_score * 0.7)
        # Parse years of experience
        from jobs.scoring_engine import ScoringEngine
        exp_years = ScoringEngine.parse_experience_years(experience)
        recruiter_score += min(15, int(exp_years * 2.0))
        
        # Check alignment with preferred roles
        pref_roles = career_preferences.get("preferred_roles", [])
        if isinstance(pref_roles, list) and pref_roles:
            role_titles = [e.get("job_title", "").lower() for e in experience]
            for p_role in pref_roles:
                if any(p_role.lower() in rt for rt in role_titles):
                    recruiter_score += 15
                    break
        recruiter_score = min(100, recruiter_score)
        
        # Build Semantic co-occurrence graph
        graph = SemanticResumeGraph.build_graph(resume)
        
        # Create Semantic tags
        semantic_tags = list(set([s.lower() for s in skills] + [t.lower() for p in projects for t in p.get("technologies", [])]))
        
        # Build final unified object
        unified_obj = {
            "resume_id": str(resume["_id"]),
            "filename": resume.get("filename", "Resume.pdf"),
            "skills": skills,
            "projects": projects,
            "experience": experience,
            "ats_score": ats_score,
            "ats_weaknesses": ats_weaknesses,
            "recruiter_score": recruiter_score,
            "career_preferences": career_preferences,
            "semantic_tags": semantic_tags[:15],
            "experience_graph": graph,
            "embeddings": resume.get("embeddings", {}),
            "achievements": resume.get("detected_strengths", ["Demonstrated engineering expertise"])
        }
        
        # Update resume record in DB with these fresh indicators
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$set": {
                "extracted_skills": skills,
                "semantic_tags": unified_obj["semantic_tags"],
                "recruiter_score": recruiter_score,
                "ATS weaknesses": ats_weaknesses,
                "ats_weaknesses": ats_weaknesses,
                "ai_context": unified_obj
            }}
        )
        
        return unified_obj
