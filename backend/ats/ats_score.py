def calculate_ats_score(
    text,
    skills,
    experience,
    education
):

    score = 0

    if len(skills) >= 5:
        score += 30

    if experience >= 2:
        score += 25

    if len(education) > 0:
        score += 20

    if "projects" in text.lower():
        score += 15

    if "certification" in text.lower():
        score += 10

    return min(score, 100)