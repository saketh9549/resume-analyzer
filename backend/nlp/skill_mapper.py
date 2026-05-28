from typing import List, Dict, Set

# Synonymous skill mappings and category associations
SKILL_SYNONYMS = {
    "react": ["reactjs", "react.js", "react framework"],
    "node.js": ["nodejs", "node", "node js"],
    "typescript": ["ts"],
    "javascript": ["js", "es6"],
    "aws": ["amazon web services", "ec2", "s3", "rds", "lambda", "cloudfront"],
    "gcp": ["google cloud", "google cloud platform", "gke", "bigquery"],
    "azure": ["microsoft azure", "azure devops"],
    "kubernetes": ["k8s", "helm", "minikube"],
    "docker": ["containers", "docker-compose", "containerization"],
    "fastapi": ["fast api", "python fastapi"],
    "rest api": ["restful api", "rest apis", "rest web services", "api development"],
    "sql": ["mysql", "postgresql", "sqlite", "mssql", "oracle sql"],
    "nosql": ["mongodb", "redis", "cassandra", "dynamodb", "couchdb"],
    "machine learning": ["ml", "deep learning", "nlp", "computer vision", "neural networks", "scikit-learn"]
}

# Contextual matches mapping general categories to specific technologies
CONTEXTUAL_TECH_MAP = {
    "rest api development": ["fastapi", "flask", "django", "express", "node.js", "spring boot", "rest api"],
    "cloud experience": ["aws", "azure", "gcp", "docker", "kubernetes", "cloud computing", "terraform"],
    "devops": ["docker", "kubernetes", "jenkins", "git", "ci/cd", "terraform", "ansible"],
    "frontend": ["react", "angular", "vue", "html", "css", "next.js", "tailwind css", "typescript"],
    "backend": ["python", "node.js", "java", "go", "c#", "fastapi", "django", "express", "sql"],
    "database": ["sql", "mysql", "postgresql", "mongodb", "redis", "nosql", "dynamodb"]
}

def resolve_skill_synonyms(skill: str) -> List[str]:
    """
    Returns a list of synonymous strings for a given skill to ensure alignment.
    """
    s_lower = skill.lower().strip()
    syns = [s_lower]
    
    # Check forward synonyms mapping
    if s_lower in SKILL_SYNONYMS:
        syns.extend(SKILL_SYNONYMS[s_lower])
        
    # Check reverse lookup
    for key, values in SKILL_SYNONYMS.items():
        if s_lower in values:
            syns.append(key)
            syns.extend([v for v in values if v != s_lower])
            break
            
    return list(set(syns))

def check_contextual_match(user_skills: List[str], required_skill: str) -> bool:
    """
    Checks if a candidate's skill set matches a general category/skill contextually.
    E.g. if required_skill is "Cloud Experience" and user has "AWS" -> returns True.
    """
    req_lower = required_skill.lower().strip()
    user_skills_lower = {s.lower().strip() for s in user_skills}
    
    # Direct match check (including synonyms)
    for us in user_skills_lower:
        if req_lower in resolve_skill_synonyms(us):
            return True
            
    # Context map check
    if req_lower in CONTEXTUAL_TECH_MAP:
        mapped_techs = CONTEXTUAL_TECH_MAP[req_lower]
        # If user has any of the specific technologies, it is a contextual match
        for tech in mapped_techs:
            if tech in user_skills_lower:
                return True
                
    # Reverse context check (if user claims a broad skill, they match specific items)
    for us in user_skills_lower:
        if us in CONTEXTUAL_TECH_MAP:
            if req_lower in CONTEXTUAL_TECH_MAP[us] or req_lower == us:
                return True
                
    return False

def extract_matched_synonyms(user_skills: List[str], required_skills: List[str]) -> List[str]:
    """
    Compiles list of user skills that overlap contextually with the job requirement.
    """
    matched = []
    for req in required_skills:
        if check_contextual_match(user_skills, req):
            matched.append(req)
    return matched
