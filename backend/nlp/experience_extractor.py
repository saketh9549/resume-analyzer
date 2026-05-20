import re

def extract_experience(text):

    pattern = r"(\d+)\+?\s+years"

    matches = re.findall(pattern, text.lower())

    if matches:
        return max([int(x) for x in matches])

    return 0