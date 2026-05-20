from backend.parsers.pdf_parser import extract_text_from_pdf

from backend.parsers.text_cleaner import clean_text

from backend.nlp.skill_extractor import extract_skills

from backend.nlp.experience_extractor import extract_experience

from backend.nlp.education_extractor import extract_education

from backend.ats.ats_score import calculate_ats_score


def analyze_resume(file_path):

    text = extract_text_from_pdf(file_path)

    cleaned_text = clean_text(text)

    skills = extract_skills(cleaned_text)

    experience = extract_experience(cleaned_text)

    education = extract_education(cleaned_text)

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