from typing import Dict, Any, List

# Core recommended list of industry keywords for software engineering
CORE_RECOMMENDED_SKILLS = ["React", "Node.js", "Python", "Docker", "AWS", "SQL", "Git", "JavaScript", "TypeScript"]

def calculate_ats_score(parsed_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """
    Computes a transparent multi-dimensional ATS score based on 10 separate NLP dimensions.
    """
    from nlp.ats_matrix import calculate_weighted_score
    from nlp.explainable_scoring import generate_explanations
    from nlp.feedback_engine import FeedbackEngine
    from nlp.action_verb_analyzer import analyze_experience_verbs
    import re
    
    skills = parsed_data.get("skills", [])
    education = parsed_data.get("education", [])
    experience = parsed_data.get("experience", [])
    projects = parsed_data.get("projects", [])
    certifications = parsed_data.get("certifications", [])
    contact = parsed_data.get("contact", {})

    # Normalize raw text
    text_lower = raw_text.lower()
    word_count = len(raw_text.split())

    # 1. SKILLS MATCH (Weight: 20%)
    core_matches = [s for s in CORE_RECOMMENDED_SKILLS if s.lower() in [sk.lower() for sk in skills]]
    missing_skills = [s for s in CORE_RECOMMENDED_SKILLS if s.lower() not in [sk.lower() for sk in skills]]
    skills_match_score = int((len(core_matches) / max(1, len(CORE_RECOMMENDED_SKILLS))) * 100.0)

    # 2. SEMANTIC RELEVANCE (Weight: 15%)
    from nlp.skill_mapper import CONTEXTUAL_TECH_MAP
    matched_cats = 0
    for cat, list_t in CONTEXTUAL_TECH_MAP.items():
        if any(t.lower() in text_lower for t in list_t):
            matched_cats += 1
    semantic_relevance_score = int((matched_cats / max(1, len(CONTEXTUAL_TECH_MAP))) * 100.0)

    # 3. EXPERIENCE QUALITY (Weight: 15%)
    experience_score = 0.0
    if experience:
        job_count = len(experience)
        bullets_count = sum(len(job.get("responsibilities", [])) for job in experience)
        experience_score += min(job_count * 25.0, 50.0)
        experience_score += min(bullets_count * 10.0, 50.0)
    experience_quality_score = int(experience_score)

    # 4. RESUME FORMATTING (Weight: 5%)
    formatting_score = 100.0
    if word_count < 250:
        formatting_score -= 30
    elif word_count > 1000:
        formatting_score -= 25
    bullet_lines = raw_text.count("•") + raw_text.count("-")
    if bullet_lines > 35:
        formatting_score -= 15
    resume_formatting_score = int(max(0.0, formatting_score))

    # 5. SECTION COMPLETENESS (Weight: 10%)
    completion_factors = {
        "email": bool(contact.get("email")),
        "phone": bool(contact.get("phone")),
        "github": bool(contact.get("github")),
        "linkedin": bool(contact.get("linkedin")),
        "experience": bool(experience),
        "education": bool(education),
        "skills": bool(skills),
        "projects": bool(projects),
        "certifications": bool(certifications)
    }
    fulfilled = sum(1 for present in completion_factors.values() if present)
    section_completeness_score = int((fulfilled / len(completion_factors)) * 100.0)

    # 6. ACTION VERB STRENGTH (Weight: 10%)
    responsibilities = []
    for exp in experience:
        responsibilities.extend(exp.get("responsibilities", []))
    verb_res = analyze_experience_verbs(responsibilities)
    action_verb_strength_score = verb_res["verb_score"]

    # 7. ACHIEVEMENT QUALITY (Weight: 10%)
    ach_sentences = 0
    total_sentences = 0
    sentences = re.split(r'[\.\!\?]', raw_text)
    for sent in sentences:
        s_clean = sent.strip()
        if not s_clean or len(s_clean.split()) < 4:
            continue
        total_sentences += 1
        if re.search(r'\b(?:\d+%\s*(?:increase|reduction|growth|improvement)|[\$\d,]+\s*(?:saved|generated|revenue)|\d+\+)\b', s_clean, re.I):
            ach_sentences += 1
    achievement_quality_score = int((ach_sentences / max(1, total_sentences)) * 100.0 * 2.5)
    achievement_quality_score = min(100, max(20, achievement_quality_score))

    # 8. READABILITY (Weight: 5%)
    avg_sentence_len = 15.0
    if total_sentences > 0:
        words_in_sents = sum(len(s.split()) for s in sentences if s.strip())
        avg_sentence_len = words_in_sents / total_sentences
    readability_score = 100.0
    if avg_sentence_len < 10:
        readability_score -= 15
    elif avg_sentence_len > 22:
        readability_score -= 25
    readability_score = int(max(20.0, readability_score))

    # 9. KEYWORD COVERAGE (Weight: 5%)
    keyword_coverage_score = min(int((len(skills) / 12) * 100.0), 100)

    # 10. RECRUITER RELEVANCE (Weight: 5%)
    from jobs.scoring_engine import ScoringEngine
    exp_years = ScoringEngine.parse_experience_years(experience)
    recruiter_relevance_score = min(100, int((exp_years / 3.0) * 100.0))
    if education:
        recruiter_relevance_score = min(100, recruiter_relevance_score + 10)

    category_scores = {
        "skills_match": skills_match_score,
        "semantic_relevance": semantic_relevance_score,
        "experience_quality": experience_quality_score,
        "resume_formatting": resume_formatting_score,
        "section_completeness": section_completeness_score,
        "action_verb_strength": action_verb_strength_score,
        "achievement_quality": achievement_quality_score,
        "readability": readability_score,
        "keyword_coverage": keyword_coverage_score,
        "recruiter_relevance": recruiter_relevance_score
    }

    final_score = calculate_weighted_score(category_scores)
    
    legacy_category_scores = {
        "skills_match": skills_match_score,
        "technical_keywords": keyword_coverage_score,
        "experience_depth": experience_quality_score,
        "education_strength": int(min(100.0, len(education) * 50.0)),
        "projects_quality": int(min(100.0, len(projects) * 50.0)),
        "resume_completeness": section_completeness_score,
        "resume_formatting": resume_formatting_score
    }

    ats_breakdown = generate_explanations(category_scores)
    feedback = FeedbackEngine.generate_feedback(parsed_data, raw_text)

    suggestions = feedback["completeness_feedback"] + feedback["action_verb_upgrades"]
    suggestions = list(dict.fromkeys(suggestions))[:4]
    if not suggestions:
        suggestions = ["Your resume matches all core checks! Tailor it further to specific job descriptions."]
        
    detected_strengths = []
    if skills_match_score >= 75:
        detected_strengths.append("High correlation with target industry keywords and core skillsets.")
    if experience_quality_score >= 75:
        detected_strengths.append("Robust professional history showing deep layout descriptions.")
    if resume_formatting_score >= 85:
        detected_strengths.append("Optimal word density and readable spacing.")
    if not detected_strengths:
        detected_strengths.append("Clean core document schema.")

    return {
        "score": final_score,
        "category_scores": legacy_category_scores,
        "ats_breakdown": ats_breakdown,
        "feedback_history": feedback,
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "detected_strengths": detected_strengths,
        "optimization_recommendations": feedback["rewrite_suggestions"] + feedback["quantification_suggestions"]
    }
