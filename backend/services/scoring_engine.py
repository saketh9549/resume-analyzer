from typing import Dict, Any, List

# Core recommended list of industry keywords for software engineering
CORE_RECOMMENDED_SKILLS = ["React", "Node.js", "Python", "Docker", "AWS", "SQL", "Git", "JavaScript", "TypeScript"]

def calculate_ats_score(parsed_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
    """
    Computes a weighted ATS score based on 7 separate dimensions.
    Returns the total score, category scores breakdown, missing skills,
    suggestions list, detected strengths, and optimization recommendations.
    """
    skills = parsed_data.get("skills", [])
    education = parsed_data.get("education", [])
    experience = parsed_data.get("experience", [])
    projects = parsed_data.get("projects", [])
    certifications = parsed_data.get("certifications", [])
    contact = parsed_data.get("contact", {})

    # Normalize raw text
    text_lower = raw_text.lower()

    # 1. SKILLS MATCH (Weight: 25%)
    # Ratio of matched core recommended skills
    core_matches = [s for s in CORE_RECOMMENDED_SKILLS if s in skills]
    missing_skills = [s for s in CORE_RECOMMENDED_SKILLS if s not in skills]
    
    if CORE_RECOMMENDED_SKILLS:
        skills_match_score = int((len(core_matches) / len(CORE_RECOMMENDED_SKILLS)) * 100)
    else:
        skills_match_score = 100

    # 2. TECHNICAL KEYWORDS (Weight: 15%)
    # Breadth of skills found (10 skills = 100%)
    tech_keywords_score = min(int((len(skills) / 10) * 100), 100)

    # 3. EXPERIENCE DEPTH (Weight: 20%)
    # Checked based on job titles, responsibilities count, and bullet descriptions
    experience_score = 0
    if experience:
        job_count = len(experience)
        # Ratio of responsibilities listed (min 3 bullet points per job)
        bullets_count = sum(len(job.get("responsibilities", [])) for job in experience)
        
        experience_score += min(job_count * 25, 50)  # max 50 points for job count (2 jobs)
        experience_score += min(bullets_count * 10, 50)  # max 50 points for bullet depth
    
    # 4. EDUCATION STRENGTH (Weight: 10%)
    # Evaluated on presence of degree items
    education_score = 0
    if education:
        has_degree = any(edu.get("degree") for edu in education)
        has_school = any(edu.get("institution") for edu in education)
        if has_degree:
            education_score += 60
        if has_school:
            education_score += 40

    # 5. PROJECTS QUALITY (Weight: 15%)
    # Rated on project count and description depth
    projects_score = 0
    if projects:
        proj_count = len(projects)
        has_desc = any(len(p.get("description", "")) > 30 for p in projects)
        
        projects_score += min(proj_count * 35, 70)  # max 70 points for count (2 projects)
        if has_desc:
            projects_score += 30

    # 6. RESUME COMPLETENESS (Weight: 10%)
    # Checks presence of contact details and core fields
    completeness_score = 0
    completion_factors = {
        "email": bool(contact.get("email")),
        "phone": bool(contact.get("phone")),
        "github": bool(contact.get("github")),
        "linkedin": bool(contact.get("linkedin")),
        "experience": bool(experience),
        "education": bool(education),
        "skills": bool(skills)
    }
    
    fulfilled = sum(1 for factor, present in completion_factors.items() if present)
    completeness_score = int((fulfilled / len(completion_factors)) * 100)

    # 7. RESUME FORMATTING (Weight: 5%)
    # Evaluated based on text length and structure density (ideal 300 to 800 words)
    word_count = len(raw_text.split())
    formatting_score = 100
    
    if word_count < 250:
        # Too sparse
        formatting_score -= 30
    elif word_count > 1000:
        # Too wordy / lacks spacing
        formatting_score -= 25
        
    # Check for excessive bullets
    bullet_lines = raw_text.count("•") + raw_text.count("-")
    if bullet_lines > 35:
        formatting_score -= 15
        
    formatting_score = max(formatting_score, 0)

    # WEIGHTED CALCULATION
    final_score = int(
        (skills_match_score * 0.25) +
        (tech_keywords_score * 0.15) +
        (experience_score * 0.20) +
        (education_score * 0.10) +
        (projects_score * 0.15) +
        (completeness_score * 0.10) +
        (formatting_score * 0.05)
    )

    # Ensure score is bound between 15% and 98%
    final_score = max(min(final_score, 98), 15)

    # STRENGTHS, SUGGESTIONS & OPTIMIZATION RECOMMENDATIONS
    detected_strengths = []
    suggestions = []
    optimization_recommendations = []

    # Strengths
    if skills_match_score >= 80:
        detected_strengths.append("High correlation with target industry keywords and core skillsets.")
    if experience_score >= 80:
        detected_strengths.append("Robust professional history showing deep layout descriptions.")
    if projects_score >= 80:
        detected_strengths.append("Structured personal/academic project outlines with technology lists.")
    if formatting_score >= 90:
        detected_strengths.append("Optimal word density and readable spacing.")
        
    if not detected_strengths:
        detected_strengths.append("Clean core document schema.")

    # Suggestions
    if not completion_factors["github"]:
        suggestions.append("Add your GitHub profile link to highlight open-source contributions.")
    if not completion_factors["linkedin"]:
        suggestions.append("Provide a professional LinkedIn profile URL.")
    if "Docker" in missing_skills or "Kubernetes" in missing_skills:
        suggestions.append("Mention containerization technologies (e.g. Docker, Kubernetes) if experienced.")
    if "AWS" in missing_skills or "Azure" in missing_skills or "GCP" in missing_skills:
        suggestions.append("Specify cloud architecture frameworks (e.g. AWS, Azure, Google Cloud).")
    if word_count < 250:
        suggestions.append("Extend your descriptions. The resume is currently too short for an ATS scan.")
    if len(skills) < 6:
        suggestions.append("List more programming languages, database structures, and frameworks under skills.")

    # Generic optimization recommendations
    optimization_recommendations.append("Incorporate more quantifiable achievements (e.g., 'saved $5,000 yearly', 'boosted API response speeds by 30%').")
    optimization_recommendations.append("Keep the resume length to a clean 1-page structure if under 5 years of experience.")
    optimization_recommendations.append("Align your project descriptions to demonstrate leadership and system architecture ownership.")

    # Dedup and cap items
    suggestions = list(dict.fromkeys(suggestions))[:4]
    if not suggestions:
        suggestions = ["Your resume matches all core checks! Tailor it further to specific job descriptions."]

    return {
        "score": final_score,
        "category_scores": {
            "skills_match": skills_match_score,
            "technical_keywords": tech_keywords_score,
            "experience_depth": experience_score,
            "education_strength": education_score,
            "projects_quality": projects_score,
            "resume_completeness": completeness_score,
            "resume_formatting": formatting_score
        },
        "missing_skills": missing_skills,
        "suggestions": suggestions,
        "detected_strengths": detected_strengths,
        "optimization_recommendations": optimization_recommendations
    }
