import re
from typing import Dict

# Map standard section keys to lists of common synonymous headings
SECTION_HEADING_SYNONYMS = {
    "contact": [
        "contact", "contact info", "contact information", "personal details", "personal info", 
        "personal information", "about me", "address", "links", "social profiles"
    ],
    "summary": [
        "professional summary", "summary", "profile", "professional profile", "career objective", 
        "executive summary", "career profile", "introduction", "about me", "overview"
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "skills & tools", "languages & frameworks",
        "technologies", "expertise", "proficiencies", "specialties", "technical expertise", "skills list"
    ],
    "experience": [
        "experience", "work experience", "professional experience", "employment history", 
        "work history", "career history", "professional history", "employment", "where i've been",
        "professional background", "experience history", "co-op experience"
    ],
    "education": [
        "education", "academic history", "academic background", "education background", 
        "degrees", "universities", "university", "credentials", "qualifications", "academic profile"
    ],
    "certifications": [
        "certifications", "licenses", "courses", "credentials", "awards & certifications", 
        "accreditations", "training", "professional development", "online courses"
    ],
    "projects": [
        "projects", "personal projects", "academic projects", "key projects", "selected projects",
        "portfolio", "technical projects", "open source contributions", "product development"
    ],
    "achievements": [
        "achievements", "accomplishments", "honors", "awards", "recognition", "successes", 
        "key achievements", "awards & honors", "distinctions"
    ],
    "publications": [
        "publications", "research", "papers", "articles", "patents", "published works",
        "conference papers", "talks"
    ],
    "languages": [
        "languages", "languages spoken", "linguistic skills", "multilingual"
    ],
    "interests": [
        "interests", "hobbies", "activities", "extracurricular activities", "extracurriculars",
        "volunteer experience", "affiliations"
    ]
}

def map_heading_to_section(heading: str) -> str:
    """
    Normalizes a section heading to one of the 11 standard keys.
    Returns the standard key if matched, or an empty string if unmatched.
    """
    clean_h = re.sub(r'[^\w\s\&\/\,\-]', '', heading.lower()).strip()
    if not clean_h:
        return ""
        
    # Check exact match first
    for key, synonyms in SECTION_HEADING_SYNONYMS.items():
        if clean_h in synonyms:
            return key
            
    # Check word overlapping or regex matching
    for key, synonyms in SECTION_HEADING_SYNONYMS.items():
        for syn in synonyms:
            # Word-level pattern matching
            if len(syn) > 3 and (syn in clean_h or clean_h in syn):
                return key
                
    return ""
