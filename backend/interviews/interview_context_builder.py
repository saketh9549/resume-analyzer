from typing import Dict, Any
from nlp.resume_context_engine import ResumeContextEngine
from nlp.ai_context_builder import AIContextBuilder

class InterviewContextBuilder:
    @staticmethod
    def build_interview_context(resume_id: str, user_email: str) -> Dict[str, Any]:
        """
        Gathers Unified Resume Intelligence context and formats it for interview prep prompt creation.
        """
        intelligence_obj = ResumeContextEngine.get_unified_context(resume_id, user_email)
        
        # Build prompt representation
        prompt_representation = AIContextBuilder.build_llm_prompt_context(intelligence_obj)
        
        return {
            "intelligence_object": intelligence_obj,
            "prompt_context": prompt_representation,
            "skills": intelligence_obj.get("skills", []),
            "ats_weaknesses": intelligence_obj.get("ats_weaknesses", []),
            "experience": intelligence_obj.get("experience", []),
            "projects": intelligence_obj.get("projects", [])
        }
