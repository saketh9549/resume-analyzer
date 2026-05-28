from typing import Dict, Any

class AIContextBuilder:
    @staticmethod
    def build_text_summary(intelligence_obj: Dict[str, Any]) -> str:
        """
        Builds a compact summary string representing the candidate's core profile.
        """
        skills = ", ".join(intelligence_obj.get("skills", []))
        
        experience_summary = []
        for exp in intelligence_obj.get("experience", []):
            role = exp.get("job_title", "Engineer")
            company = exp.get("company", "Company")
            responsibilities = ". ".join(exp.get("responsibilities", []))
            experience_summary.append(f"{role} at {company}: {responsibilities}")
            
        projects_summary = []
        for proj in intelligence_obj.get("projects", []):
            name = proj.get("name", "Project")
            desc = proj.get("description", "")
            tech = ", ".join(proj.get("technologies", []))
            projects_summary.append(f"{name} ({tech}): {desc}")
            
        summary = f"""
        Candidate Skills: {skills}
        Professional History: {' | '.join(experience_summary)}
        Projects: {' | '.join(projects_summary)}
        """
        return summary.strip()

    @staticmethod
    def build_llm_prompt_context(intelligence_obj: Dict[str, Any]) -> str:
        """
        Builds a structured markdown prompt context block for Gemini calls.
        """
        pref = intelligence_obj.get("career_preferences", {})
        pref_roles = ", ".join(pref.get("preferred_roles", [])) if isinstance(pref.get("preferred_roles"), list) else pref.get("preferred_roles", "")
        pref_tech = ", ".join(pref.get("preferred_technologies", [])) if isinstance(pref.get("preferred_technologies"), list) else pref.get("preferred_technologies", "")
        pref_industries = ", ".join(pref.get("preferred_industries", [])) if isinstance(pref.get("preferred_industries"), list) else pref.get("preferred_industries", "")
        
        context = f"""
### Candidate Profile & Experience Graph
- **Name/Filename**: {intelligence_obj.get("filename", "Candidate Resume")}
- **ATS Score**: {intelligence_obj.get("ats_score", 0)}%
- **Recruiter Score**: {intelligence_obj.get("recruiter_score", 0)}/100
- **Skills & Technologies**: {', '.join(intelligence_obj.get("skills", []))}
- **ATS Weaknesses & Missing Skills**: {', '.join(intelligence_obj.get("ats_weaknesses", []))}

### Professional Experience
"""
        for exp in intelligence_obj.get("experience", []):
            context += f"- **{exp.get('job_title', 'Role')}** at *{exp.get('company', 'Company')}* ({exp.get('duration', 'N/A')})\n"
            for resp in exp.get('responsibilities', []):
                context += f"  - {resp}\n"
                
        context += "\n### Key Projects\n"
        for proj in intelligence_obj.get("projects", []):
            context += f"- **{proj.get('name', 'Project')}** (Tech: {', '.join(proj.get('technologies', []))}):\n"
            context += f"  - {proj.get('description', '')}\n"
            
        context += f"""
### Career preferences & Alignment
- **Preferred Roles**: {pref_roles or 'N/A'}
- **Preferred Technologies**: {pref_tech or 'N/A'}
- **Preferred Industries**: {pref_industries or 'N/A'}
- **Expected Level**: {pref.get('experience_level', 'N/A')}
- **Remote / Location Preference**: {pref.get('remote_preference', 'N/A')} ({pref.get('location_preference', 'N/A')})
"""
        return context.strip()
