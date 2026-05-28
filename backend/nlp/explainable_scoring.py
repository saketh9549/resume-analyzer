from typing import Dict, List, Any

CATEGORY_METADATA = {
    "skills_match": {
        "title": "Skills Match",
        "description": "Checks the alignment of your declared skills against target job description requirements.",
        "tip_high": "Excellent coverage of core technical requirements.",
        "tip_low": "Identify missing tech keywords and insert them in your skills matrix."
    },
    "semantic_relevance": {
        "title": "Semantic Relevance",
        "description": "Evaluates structural conceptual overlap and topic matching.",
        "tip_high": "Strong semantic alignment with targeted roles.",
        "tip_low": "Rephrase bullet points to emphasize key industry concepts and technologies."
    },
    "experience_quality": {
        "title": "Experience Quality",
        "description": "Reviews the depth of detail, job count, and bullet counts in work history.",
        "tip_high": "Detailed professional history with deep layout descriptions.",
        "tip_low": "Ensure at least 3 bullet points per job detailing exact achievements."
    },
    "resume_formatting": {
        "title": "Resume Formatting",
        "description": "Checks word count, layout density, and proper section spacing.",
        "tip_high": "Optimal text density and clean layouts.",
        "tip_low": "Keep total word count between 300 and 800 words and limit bullet lists."
    },
    "section_completeness": {
        "title": "Section Completeness",
        "description": "Checks for presence of standard sections like summary, experience, and contact details.",
        "tip_high": "All standard resume sections fully populated.",
        "tip_low": "Add missing sections such as Projects or Certifications to enrich your profile."
    },
    "action_verb_strength": {
        "title": "Action Verb Strength",
        "description": "Measures usage of weak verbs (helped, worked) vs strong verbs (engineered, spear-headed).",
        "tip_high": "Great use of active, impactful vocabulary.",
        "tip_low": "Upgrade passive words (e.g. 'helped with') to action-oriented verbs."
    },
    "achievement_quality": {
        "title": "Achievement Quality",
        "description": "Scans sentences for quantifiable metrics (percentages, revenue, numbers).",
        "tip_high": "Excellent use of metrics to demonstrate impact.",
        "tip_low": "Quantify outcomes (e.g., 'improved page speed by 40%', 'managed $5k budget')."
    },
    "readability": {
        "title": "Readability",
        "description": "Computes structural word complexity and sentence lengths.",
        "tip_high": "Highly readable, punchy sentence layouts.",
        "tip_low": "Shorten long, convoluted sentences to improve ATS parsing."
    },
    "keyword_coverage": {
        "title": "Keyword Coverage",
        "description": "Measures total technical keyword count and density distributions.",
        "tip_high": "Broad technical keyword coverage.",
        "tip_low": "Add more domain-relevant terms to improve indexing on search engines."
    },
    "recruiter_relevance": {
        "title": "Recruiter Relevance",
        "description": "Aligns years of experience and candidate roles to recruiter requirements.",
        "tip_high": "Target qualifications strongly match expectations.",
        "tip_low": "Tailor your professional headlines to match the recruiter's exact role title."
    }
}

def generate_explanations(category_scores: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Constructs explainable score cards for the 10 dimensions.
    """
    breakdown = []
    
    for key, meta in CATEGORY_METADATA.items():
        score = int(category_scores.get(key, 0.0))
        
        # Determine specific feedback tip based on score
        tip = meta["tip_high"] if score >= 75 else meta["tip_low"]
        
        breakdown.append({
            "category": key,
            "title": meta["title"],
            "description": meta["description"],
            "score": score,
            "tip": tip,
            "status": "strength" if score >= 75 else ("warning" if score >= 50 else "critical")
        })
        
    return breakdown
