import os
import re
import pdfplumber

# List of common industry skills mapped from their search patterns to display names
SKILL_KEYWORDS = {
    # Programming Languages
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "c\\+\\+": "C++",
    "c#": "C#",
    "go|golang": "Go",
    "ruby": "Ruby",
    "php": "PHP",
    "rust": "Rust",
    "html5?": "HTML",
    "css3?": "CSS",
    # Frameworks / Libraries
    "react": "React",
    "angular": "Angular",
    "vue": "Vue",
    "next\\.js": "Next.js",
    "node\\.js": "Node.js",
    "express": "Express",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring boot": "Spring Boot",
    "pandas": "Pandas",
    "numpy": "Numpy",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    # Tools / Cloud / DevOps
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "git": "Git",
    "jenkins": "Jenkins",
    "ci/cd": "CI/CD",
    "terraform": "Terraform",
    # Databases
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "oracle": "Oracle",
    # Concepts
    "rest api": "REST APIs",
    "graphql": "GraphQL",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "data structures": "Data Structures",
    "algorithms": "Algorithms"
}

# Industry standard recommended skills for full-stack software developers
RECOMMENDED_SKILLS = ["React", "Node.js", "Python", "Docker", "AWS", "SQL", "Git", "JavaScript", "TypeScript"]

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber page by page.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def analyze_resume_text(text: str):
    """
    Scans the text for skills, structures, and section headers to calculate
    an ATS matching score and output list of found skills, missing skills, and suggestions.
    """
    if not text or not text.strip():
        return {
            "score": 45,
            "skills_found": [],
            "missing_skills": RECOMMENDED_SKILLS[:5],
            "suggestions": [
                "Could not extract text. Please check if the PDF is scanned/image-only.",
                "Ensure your PDF resume contains readable machine-copyable text.",
                "Create clear sections for Work Experience, Education, and Skills."
            ]
        }

    normalized_text = text.lower()
    skills_found = []

    # Match skills using boundary regexes
    for pattern, display_name in SKILL_KEYWORDS.items():
        # Determine if the character at the start/end is alphanumeric to apply word boundaries correctly
        # This ensures patterns like 'c++' or 'c#' match without being blocked by word boundaries on non-word characters.
        clean_pattern = pattern.replace('\\', '')
        
        # Handle OR patterns correctly by checking boundaries of the first and last alternative
        parts = clean_pattern.split('|')
        start_char = parts[0][0] if parts[0] else ''
        end_char = parts[-1][-1] if parts[-1] else ''
        
        start_boundary = r'\b' if start_char.isalnum() else ''
        end_boundary = r'\b' if end_char.isalnum() else ''

        regex_pattern = start_boundary + (f"({pattern})" if '|' in pattern else pattern) + end_boundary
        if re.search(regex_pattern, normalized_text):
            if display_name not in skills_found:
                skills_found.append(display_name)


    # Determine which of the recommended core skills are missing
    missing_skills = [skill for skill in RECOMMENDED_SKILLS if skill not in skills_found]

    # Scorer formula:
    # 1. Skill breadth (max 60 points): 6 points per found skill up to 10 skills.
    skill_points = min((len(skills_found) / 10) * 60, 60)

    # 2. Page structures & key sections presence (max 40 points):
    sections = {
        "experience": ["experience", "work history", "employment", "professional history"],
        "education": ["education", "academic", "university", "college", "degree"],
        "projects": ["projects", "personal projects", "portfolio"],
        "skills": ["skills", "technologies", "technical skills", "expertise"]
    }

    section_points = 0
    missing_sections = []
    for section, keywords in sections.items():
        found = False
        for keyword in keywords:
            if keyword in normalized_text:
                found = True
                break
        if found:
            section_points += 10
        else:
            missing_sections.append(section)

    total_score = int(skill_points + section_points)
    # Normalize values between 15% and 98%
    total_score = max(min(total_score, 98), 15)

    # Compile helpful engineering suggestions
    suggestions = []
    if len(skills_found) < 5:
        suggestions.append("List more specific technical tools, frameworks, and programming languages.")

    for sec in missing_sections:
        suggestions.append(f"Add a clear, separate section for '{sec.capitalize()}'.")

    # Cloud/containers checks
    if not any(x in skills_found for x in ["Docker", "Kubernetes", "AWS", "Azure", "GCP"]):
        suggestions.append("Integrate modern containerization or cloud services (e.g. AWS, Docker, Azure).")
    
    # Databases checks
    if not any(x in skills_found for x in ["MySQL", "PostgreSQL", "MongoDB", "Redis"]):
        suggestions.append("Add experience working with databases (SQL or NoSQL).")

    if "Git" not in skills_found:
        suggestions.append("Mention git version control under your toolsets.")

    suggestions.append("Incorporate quantifiable impact (e.g. 'boosted response time by 40%') rather than descriptive tasks.")
    suggestions.append("Ensure your contact detail fields (GitHub, LinkedIn, Email) are easily crawlable at the top.")

    # Deduplicate and cap to 5 suggestions
    final_suggestions = list(dict.fromkeys(suggestions))[:5]

    return {
        "score": total_score,
        "skills_found": skills_found,
        "missing_skills": missing_skills,
        "suggestions": final_suggestions
    }
