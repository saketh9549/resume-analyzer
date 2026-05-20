def extract_education(text):

    education_keywords = [
        "b.tech",
        "m.tech",
        "bachelor",
        "master",
        "phd"
    ]

    found = []

    for edu in education_keywords:

        if edu in text.lower():
            found.append(edu)

    return found