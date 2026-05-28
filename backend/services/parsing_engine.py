import re
from typing import Dict, Any, List

# Core technical skills to search for and normalize
SKILL_KEYWORDS = {
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
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "git": "Git",
    "jenkins": "Jenkins",
    "ci/cd": "CI/CD",
    "terraform": "Terraform",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "sqlite": "SQLite",
    "oracle": "Oracle",
    "rest api": "REST APIs",
    "graphql": "GraphQL",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning"
}

def clean_text(text: str) -> str:
    """
    Cleans text of extra spacing while retaining line breaks.
    """
    lines = [line.strip() for line in text.split("\n")]
    return "\n".join([line for line in lines if line])

def segment_sections(text: str) -> Dict[str, str]:
    """
    Segments the resume text into logical sections based on common headings.
    """
    normalized_text = clean_text(text)
    lines = normalized_text.split("\n")
    
    sections = {
        "contact": "",
        "experience": "",
        "education": "",
        "projects": "",
        "skills": "",
        "certifications": ""
    }
    
    # Headers regex patterns
    headers = {
        "experience": r'\b(work\s+experience|experience|employment|work\s+history|professional\s+experience|professional\s+history)\b',
        "education": r'\b(education|academic\s+background|academic\s+history|qualification|university|credentials)\b',
        "projects": r'\b(projects|personal\s+projects|academic\s+projects|portfolio)\b',
        "skills": r'\b(skills|technical\s+skills|skills\s+&\s+tools|languages\s+&\s+tools|technologies|expertise)\b',
        "certifications": r'\b(certifications|certifications\s+&\s+courses|courses|awards|credentials)\b'
    }
    
    current_section = "contact"
    section_buffers = {k: [] for k in sections.keys()}
    
    for line in lines:
        line_lower = line.lower()
        matched = False
        for sec, pattern in headers.items():
            if re.search(pattern, line_lower) and len(line.split()) < 5:
                current_section = sec
                matched = True
                break
        if not matched:
            section_buffers[current_section].append(line)
            
    for sec in sections.keys():
        sections[sec] = "\n".join(section_buffers[sec])
        
    return sections

def parse_contact_info(text: str) -> Dict[str, Any]:
    """
    Extracts basic contact fields (email, phone, github, linkedin).
    """
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""
    
    phone_match = re.search(r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b', text)
    phone = phone_match.group(0) if phone_match else ""
    
    github_match = re.search(r'github\.com/[\w\.-]+', text, re.I)
    github = github_match.group(0) if github_match else ""
    
    linkedin_match = re.search(r'linkedin\.com/in/[\w\.-]+', text, re.I)
    linkedin = linkedin_match.group(0) if linkedin_match else ""
    
    return {
        "email": email,
        "phone": phone,
        "github": github,
        "linkedin": linkedin
    }

def parse_skills(text: str) -> List[str]:
    """
    Identifies matched skills from the skill dictionary, applying boundaries safely.
    """
    skills_found = []
    text_lower = text.lower()
    
    for pattern, display_name in SKILL_KEYWORDS.items():
        clean_pattern = pattern.replace('\\', '')
        parts = clean_pattern.split('|')
        start_char = parts[0][0] if parts[0] else ''
        end_char = parts[-1][-1] if parts[-1] else ''
        
        start_boundary = r'\b' if start_char.isalnum() else ''
        end_boundary = r'\b' if end_char.isalnum() else ''
        
        regex_pattern = start_boundary + (f"({pattern})" if '|' in pattern else pattern) + end_boundary
        if re.search(regex_pattern, text_lower):
            if display_name not in skills_found:
                skills_found.append(display_name)
                
    return skills_found

def parse_education(text: str) -> List[Dict[str, str]]:
    """
    Parses education items from the education text block.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    educations = []
    
    degree_pattern = r'\b(bachelor|master|doctor|ph\.?d|b\.?s|m\.?s|b\.?tech|m\.?tech|m\.?b\.?a|diploma|associate|degree|b\.sc|m\.sc)\b'
    year_pattern = r'\b(19\d{2}|20[0-2]\d)\b'
    
    for line in lines:
        if re.search(degree_pattern, line, re.I):
            degree_match = re.search(degree_pattern, line, re.I)
            degree = degree_match.group(0) if degree_match else "Degree"
            
            years = re.findall(year_pattern, line)
            year = years[-1] if years else ""
            
            # Simple heuristic for institution: text remaining in the line minus degree & year
            clean_line = line
            clean_line = re.sub(degree_pattern, '', clean_line, flags=re.I)
            clean_line = re.sub(year_pattern, '', clean_line)
            clean_line = re.sub(r'[\-\(\),\|]', '', clean_line).strip()
            
            institution = clean_line if clean_line else "University"
            if len(institution) > 60:
                institution = institution[:60] + "..."
                
            educations.append({
                "degree": degree.capitalize() if len(degree) > 4 else degree.upper(),
                "institution": institution,
                "year": year
            })
            
    # Default fallback if structure is sparse
    if not educations and text.strip():
        educations.append({
            "degree": "Parsed Degree",
            "institution": "University / Institution",
            "year": ""
        })
        
    return educations

def parse_experience(text: str) -> List[Dict[str, Any]]:
    """
    Parses work experience from the experience text block.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    experiences = []
    
    # Common job titles keywords
    title_keywords = r'\b(engineer|developer|lead|manager|architect|analyst|intern|scientist|consultant|specialist|officer|programmer)\b'
    duration_pattern = r'\b((?:19|20)\d{2}\s*[-–]\s*(?:(?:19|20)\d{2}|present))\b'
    
    current_job = None
    
    for line in lines:
        # Check if line looks like a job header (contains title or date duration)
        has_title = re.search(title_keywords, line, re.I)
        has_duration = re.search(duration_pattern, line, re.I)
        
        if (has_title or has_duration) and len(line.split()) < 8 and not line.startswith("-") and not line.startswith("•"):
            if current_job:
                experiences.append(current_job)
                
            duration_match = re.search(duration_pattern, line, re.I)
            duration = duration_match.group(0) if duration_match else ""
            
            clean_line = re.sub(duration_pattern, '', line)
            clean_line = re.sub(r'[\-\(\),\|]', '', clean_line).strip()
            
            # Split to infer company and title
            parts = [p.strip() for p in clean_line.split("  ") if p.strip()]
            if not parts:
                parts = [p.strip() for p in clean_line.split(" at ") if p.strip()]
            if not parts:
                parts = [clean_line]
                
            job_title = parts[0] if parts else "Software Engineer"
            company = parts[1] if len(parts) > 1 else "Technology Corp"
            
            current_job = {
                "job_title": job_title,
                "company": company,
                "duration": duration,
                "responsibilities": []
            }
        elif current_job:
            # Accumulate bullet points
            if line.startswith("-") or line.startswith("•") or line.startswith("*"):
                bullet = re.sub(r'^[\-•\*]\s*', '', line)
                current_job["responsibilities"].append(bullet)
            elif len(current_job["responsibilities"]) < 5:
                current_job["responsibilities"].append(line)
                
    if current_job:
        experiences.append(current_job)
        
    # Default fallback
    if not experiences and text.strip():
        experiences.append({
            "job_title": "Professional Experience",
            "company": "Company / Employer",
            "duration": "",
            "responsibilities": [line[:100] for line in lines[:3]]
        })
        
    return experiences

def parse_projects(text: str) -> List[Dict[str, Any]]:
    """
    Parses personal/academic projects from the projects block.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    projects = []
    
    current_proj = None
    
    for line in lines:
        # Check if line looks like project header
        if len(line.split()) < 5 and not line.startswith("-") and not line.startswith("•") and not line.startswith("*"):
            if current_proj:
                projects.append(current_proj)
            current_proj = {
                "name": line,
                "description": "",
                "technologies": []
            }
        elif current_proj:
            if line.startswith("-") or line.startswith("•") or line.startswith("*"):
                bullet = re.sub(r'^[\-•\*]\s*', '', line)
                if not current_proj["description"]:
                    current_proj["description"] = bullet
                else:
                    current_proj["description"] += " " + bullet
            else:
                if not current_proj["description"]:
                    current_proj["description"] = line
                else:
                    current_proj["description"] += " " + line
                    
    if current_proj:
        projects.append(current_proj)
        
    # Extract technologies from description
    for proj in projects:
        proj["technologies"] = parse_skills(proj["description"])
        
    # Fallback
    if not projects and text.strip():
        projects.append({
            "name": "Personal Project",
            "description": "Implemented software solutions using modern technologies.",
            "technologies": []
        })
        
    return projects

def parse_certifications(text: str) -> List[str]:
    """
    Parses certifications arrays from certifications block.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    certs = []
    
    cert_keywords = r'\b(certified|certification|certificate|scrummaster|aws|cisco|comptia|pmp|udemy|coursera)\b'
    
    for line in lines:
        if re.search(cert_keywords, line, re.I):
            certs.append(line)
        elif line.startswith("-") or line.startswith("•"):
            bullet = re.sub(r'^[\-•]\s*', '', line)
            certs.append(bullet)
            
    return list(dict.fromkeys(certs))[:8]

def parse_resume(text: str) -> Dict[str, Any]:
    """
    Orchestrates parsing of text and compiles a clean, structured JSON response.
    """
    from nlp.section_classifier import SectionClassifier
    from nlp.entity_extractor import EntityExtractor
    
    seg_res = SectionClassifier.segment_resume(text)
    sections = seg_res["sections"]
    confidences = seg_res["confidences"]
    diagnostics = seg_res["diagnostics"]
    
    contact_text = sections.get("contact", "")
    skills_text = sections.get("skills", "")
    education_text = sections.get("education", "")
    experience_text = sections.get("experience", "")
    projects_text = sections.get("projects", "")
    certifications_text = sections.get("certifications", "")
    
    contact = parse_contact_info(contact_text)
    skills = parse_skills(skills_text)
    if not skills:
        skills = parse_skills(text)
        
    education = parse_education(education_text)
    experience = parse_experience(experience_text)
    projects = parse_projects(projects_text)
    certifications = parse_certifications(certifications_text)
    
    # Run NER
    extractor = EntityExtractor()
    extracted_entities = extractor.extract_all_entities(text)
    
    # Merge skills from both sources to ensure maximum density
    ner_skills = [s["value"] for s in extracted_entities.get("skills", [])]
    merged_skills = list(set(skills + ner_skills))
    
    return {
        "contact": contact,
        "skills": merged_skills,
        "education": education,
        "experience": experience,
        "projects": projects,
        "certifications": certifications,
        "extracted_entities": extracted_entities,
        "section_confidences": confidences,
        "section_diagnostics": diagnostics
    }
