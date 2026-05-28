from typing import Dict

# Dictionary mapping raw entity keywords to canonical titles
CANONICAL_ENTITIES = {
    # Programming Languages
    "py": "Python",
    "python": "Python",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "golang": "Go",
    "go": "Go",
    "cpp": "C++",
    "c++": "C++",
    "csharp": "C#",
    "c#": "C#",
    
    # Frameworks
    "reactjs": "React",
    "react.js": "React",
    "react": "React",
    "angularjs": "Angular",
    "angular": "Angular",
    "vuejs": "Vue",
    "vue": "Vue",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "spring boot": "Spring Boot",
    
    # Cloud Platforms
    "aws": "AWS",
    "amazon web services": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    
    # Databases
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    
    # Tools / Containerization
    "docker": "Docker",
    "k8s": "Kubernetes",
    "kubernetes": "Kubernetes",
    "git": "Git",
    "terraform": "Terraform"
}

def canonicalize_entity(raw_name: str) -> str:
    """
    Returns the canonical, standardized display name of a technology or skill,
    or the capitalized raw name if no mapping is found.
    """
    cleaned = raw_name.lower().strip()
    if not cleaned:
        return ""
        
    if cleaned in CANONICAL_ENTITIES:
        return CANONICAL_ENTITIES[cleaned]
        
    return raw_name.strip()
