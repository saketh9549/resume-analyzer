import re
from typing import List, Dict

class SemanticMatcher:
    @staticmethod
    def calculate_text_overlap(user_text: str, target_keywords: List[str]) -> float:
        """
        Calculates Jaccard-like similarity of target keywords inside the candidate text.
        
        Returns:
            float: percentage of keywords found (0 to 100)
        """
        if not user_text or not target_keywords:
            return 0.0
            
        # Clean text
        normalized_text = re.sub(r'[^\w\s]', '', user_text.lower())
        words = set(normalized_text.split())
        
        found = 0
        for kw in target_keywords:
            normalized_kw = re.sub(r'[^\w\s]', '', kw.lower()).strip()
            if not normalized_kw:
                continue
            
            # Simple keyword match or substring match
            if normalized_kw in words or any(normalized_kw in w for w in words):
                found += 1
                
        total_kws = len([k for k in target_keywords if k.strip()])
        return round((found / total_kws * 100.0), 1) if total_kws > 0 else 0.0

    @classmethod
    def match_projects_and_experience(
        cls, 
        projects: List[Dict], 
        experience: List[Dict], 
        job_details: Dict
    ) -> Dict:
        """
        Compares project and experience fields with job responsibilities and skills.
        """
        # Aggregate user details
        proj_text = " ".join([
            f"{p.get('title', '')} {p.get('description', '')} {' '.join(p.get('technologies', []))}"
            for p in projects
        ])
        
        exp_text = " ".join([
            f"{e.get('role', '')} {e.get('company', '')} {e.get('description', '')}"
            for e in experience
        ])
        
        # Combine matching targets
        targets = job_details.get("required_skills", []) + job_details.get("responsibilities", [])
        
        proj_score = cls.calculate_text_overlap(proj_text, targets)
        exp_score = cls.calculate_text_overlap(exp_text, targets)
        
        # Average score
        overall_semantic_score = (proj_score + exp_score) / 2.0 if (proj_text or exp_text) else 0.0
        
        return {
            "projects_alignment": round(proj_score, 1),
            "experience_alignment": round(exp_score, 1),
            "overall_semantic_score": round(overall_semantic_score, 1)
        }
