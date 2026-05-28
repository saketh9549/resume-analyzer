from typing import Dict

# Weights mapping for the 10 ATS scoring categories (must sum to 1.0)
ATS_CATEGORY_WEIGHTS = {
    "skills_match": 0.20,
    "semantic_relevance": 0.15,
    "experience_quality": 0.15,
    "resume_formatting": 0.05,
    "section_completeness": 0.10,
    "action_verb_strength": 0.10,
    "achievement_quality": 0.10,
    "readability": 0.05,
    "keyword_coverage": 0.05,
    "recruiter_relevance": 0.05
}

def calculate_weighted_score(category_scores: Dict[str, float]) -> int:
    """
    Computes aggregated weighted score based on the 10 dimensions.
    """
    total = 0.0
    for category, weight in ATS_CATEGORY_WEIGHTS.items():
        score = category_scores.get(category, 0.0)
        total += score * weight
        
    # Clamp score between 10 and 99
    return int(max(10.0, min(99.0, total)))
