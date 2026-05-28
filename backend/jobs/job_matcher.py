import os
import json
import logging
from typing import List, Dict, Any

from jobs.scoring_engine import ScoringEngine
from jobs.recommendation_engine import JobRecommendationEngine

logger = logging.getLogger(__name__)

class JobMatcherCoordinator:
    @staticmethod
    def _load_job_dataset() -> List[Dict[str, Any]]:
        """
        Loads the static job dataset from the datasets directory.
        """
        dataset_path = os.path.join(
            os.path.dirname(__file__), 
            "datasets", 
            "jobs_dataset.json"
        )
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read static jobs dataset: {e}")
            return []

    @classmethod
    async def match_resume_to_jobs(
        cls, 
        resume_data: Dict[str, Any], 
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates full matching evaluation against the job dataset.
        
        Returns:
            Dict containing:
                - recommended_jobs (List[Dict]): Evaluated matches sorted by compatibility percentage
                - career_guidance (Dict): AI recommendations
        """
        jobs = cls._load_job_dataset()
        if not jobs:
            return {
                "recommended_jobs": [],
                "career_guidance": {}
            }

        evaluated_matches = []
        
        # Load preferences
        pref_industries = [ind.strip().lower() for ind in preferences.get("preferred_industries", [])] if preferences else []
        pref_roles = [role.strip().lower() for role in preferences.get("preferred_roles", [])] if preferences else []
        pref_level = preferences.get("experience_level", "").strip().lower() if preferences else ""

        from nlp.semantic_match_engine import SemanticMatchEngine

        for job in jobs:
            # 1. Run scoring engine
            legacy_res = ScoringEngine.evaluate_job_match(resume_data, job)
            
            # 2. Run semantic match engine
            semantic_res = await SemanticMatchEngine.match_resume_to_job(
                resume_data=resume_data,
                job_details=job,
                raw_text=resume_data.get("parsed_text", "")
            )
            
            # Merge results
            match_res = {**legacy_res, **semantic_res}
            
            # 3. Preference boosts
            score = float(semantic_res["overall_score"])
            
            # Match preferred industries
            if job.get("industry", "").lower() in pref_industries or any(t.lower() in pref_industries for t in job.get("industry_tags", [])):
                score += 8.0
            
            # Match preferred roles
            if any(p_role in job.get("job_title", "").lower() for p_role in pref_roles):
                score += 10.0
                
            # Match preferred level
            if pref_level and job.get("experience_level", "").lower() == pref_level:
                score += 5.0

            # Capping final score
            match_res["match_percentage"] = min(100, int(score))
            
            # Recalculate readiness based on boosted score
            if match_res["match_percentage"] >= 85:
                match_res["readiness_level"] = "Excellent Fit"
            elif match_res["match_percentage"] >= 70:
                match_res["readiness_level"] = "Strong Alignment"
            elif match_res["match_percentage"] >= 50:
                match_res["readiness_level"] = "Potential Fit"
            else:
                match_res["readiness_level"] = "Needs Upskilling"

            evaluated_matches.append(match_res)

        # Sort jobs by match score descending
        evaluated_matches.sort(key=lambda x: x["match_percentage"], reverse=True)

        # Generate AI Career Coach guidance based on candidate profile and top 3 roles
        guidance = await JobRecommendationEngine.generate_career_guidance(
            resume_data=resume_data,
            preferences=preferences
        )

        return {
            "recommended_jobs": evaluated_matches[:6],  # Return top 6 roles
            "career_guidance": guidance
        }
