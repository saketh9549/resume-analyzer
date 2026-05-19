def match_job_description(
    resume_text,
    job_description
):

    resume_words = set(resume_text.lower().split())

    jd_words = set(job_description.lower().split())

    matched_words = resume_words.intersection(jd_words)

    score = (
        len(matched_words)
        /
        len(jd_words)
    ) * 100

    return round(score, 2)