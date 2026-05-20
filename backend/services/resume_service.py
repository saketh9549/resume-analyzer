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

""""""

def save_resume_analysis(
    user_id,
    result
):

    connection = get_connection()

    cursor = connection.cursor()

    query = """
    INSERT INTO resumes
    (
        user_id,
        resume_text,
        summary,
        total_experience,
        education
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        user_id,
        result["text"],
        "AI Generated Summary",
        result["experience"],
        ",".join(result["education"])
    )

    cursor.execute(query, values)

    connection.commit()

    resume_id = cursor.lastrowid

    # -----------------------------------
    # SAVE SKILLS
    # -----------------------------------

    for skill in result["skills"]:

        skill_query = """
        INSERT INTO resume_skills
        (
            resume_id,
            skill_name
        )
        VALUES (%s, %s)
        """

        cursor.execute(
            skill_query,
            (resume_id, skill)
        )

    # -----------------------------------
    # SAVE ATS SCORE
    # -----------------------------------

    ats_query = """
    INSERT INTO resume_scores
    (
        resume_id,
        overall_score
    )
    VALUES (%s, %s)
    """

    cursor.execute(
        ats_query,
        (
            resume_id,
            result["ats_score"]
        )
    )

    connection.commit()

    cursor.close()
    connection.close()