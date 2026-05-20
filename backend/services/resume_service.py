from backend.parsers.pdf_parser import extract_text_from_pdf

from backend.parsers.text_cleaner import clean_text

from backend.nlp.skill_extractor import extract_skills

from backend.nlp.experience_extractor import extract_experience

from backend.nlp.education_extractor import extract_education

from backend.ats.ats_score import calculate_ats_score

from database.db import get_connection


def analyze_resume(file_path):

    # --------------------------------
    # Extract Text
    # --------------------------------

    text = extract_text_from_pdf(file_path)

    # --------------------------------
    # Clean Text
    # --------------------------------

    cleaned_text = clean_text(text)

    # --------------------------------
    # Extract Skills
    # --------------------------------

    skills = extract_skills(cleaned_text)

    # --------------------------------
    # Extract Experience
    # --------------------------------

    experience = extract_experience(cleaned_text)

    # --------------------------------
    # Extract Education
    # --------------------------------

    education = extract_education(cleaned_text)

    # --------------------------------
    # ATS Score
    # --------------------------------

    ats_score = calculate_ats_score(
        cleaned_text,
        skills,
        experience,
        education
    )

    return {
        "text": cleaned_text,
        "skills": skills,
        "experience": experience,
        "education": education,
        "ats_score": ats_score
    }