from typing import List, Dict, Set

class SkillMatcher:
    @staticmethod
    def match_skills(user_skills: List[str], required_skills: List[str]) -> Dict:
        """
        Performs case-insensitive matching of user skills against required job skills.
        
        Returns:
            Dict containing:
                - matching_skills (List[str]): Original required skills that matched
                - missing_skills (List[str]): Required skills that were not matched
                - extra_skills (List[str]): User skills that weren't required but are present
                - match_ratio (float): Percentage of required skills the user possesses (0 to 100)
        """
        # Normalize to lower-case for comparison, keeping a map to original case
        user_normalized = {skill.strip().lower(): skill for skill in user_skills if skill.strip()}
        req_normalized = {skill.strip().lower(): skill for skill in required_skills if skill.strip()}
        
        user_set = set(user_normalized.keys())
        req_set = set(req_normalized.keys())
        
        # Intersections & Differences
        matching_keys = user_set.intersection(req_set)
        missing_keys = req_set.difference(user_set)
        extra_keys = user_set.difference(req_set)
        
        # Map back to original casing (preferring job spec casing for required, user casing for extra)
        matching_skills = [req_normalized[key] for key in sorted(matching_keys)]
        missing_skills = [req_normalized[key] for key in sorted(missing_keys)]
        extra_skills = [user_normalized[key] for key in sorted(extra_keys)]
        
        # Calculate ratio
        total_required = len(req_set)
        match_ratio = (len(matching_keys) / total_required * 100) if total_required > 0 else 100.0
        
        return {
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "extra_skills": extra_skills,
            "match_ratio": round(match_ratio, 1)
        }
