from typing import List, Dict

# Database of standard weak phrase rewrites
REWRITE_PAIRS = [
    {
        "phrase": "worked on backend",
        "suggestion": "Engineered scalable backend services handling 10K+ concurrent requests/day using FastAPI and PostgreSQL.",
        "category": "Backend Development"
    },
    {
        "phrase": "helped with frontend",
        "suggestion": "Spearheaded frontend component migrations to React, increasing page load performance by 35%.",
        "category": "Frontend Development"
    },
    {
        "phrase": "responsible for deployment",
        "suggestion": "Automated multi-stage CI/CD pipelines deploying containerized microservices to AWS via Docker, reducing deployment time by 45%.",
        "category": "DevOps & Cloud"
    },
    {
        "phrase": "did bug fixing",
        "suggestion": "Resolved 50+ critical system vulnerabilities, bolstering API reliability and increasing uptime to 99.99%.",
        "category": "Reliability"
    },
    {
        "phrase": "involved in project management",
        "suggestion": "Coordinated cross-functional engineering sprints using Scrum, accelerating feature delivery times by 20%.",
        "category": "Management"
    },
    {
        "phrase": "wrote unit tests",
        "suggestion": "Authored comprehensive test suites spanning 150+ unit/integration specs, boosting test coverage from 60% to 92%.",
        "category": "Testing"
    },
    {
        "phrase": "managed database",
        "suggestion": "Optimized complex query execution paths and database indexing parameters, slashing query latency by 50%.",
        "category": "Database"
    }
]

def find_rewrite_suggestions(text: str) -> List[Dict[str, str]]:
    """
    Scans the given text for passive/weak sentences and returns matched rewrite suggestions.
    """
    suggestions = []
    text_lower = text.lower()
    
    for pair in REWRITE_PAIRS:
        if pair["phrase"] in text_lower:
            suggestions.append({
                "original": f"... {pair['phrase']} ...",
                "recommended": pair["suggestion"],
                "category": pair["category"]
            })
            
    return suggestions
