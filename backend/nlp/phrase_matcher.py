import re
from typing import List, Set

COMMON_TECH_PHRASES = [
    "machine learning", "deep learning", "artificial intelligence", "natural language processing",
    "computer vision", "neural networks", "data science", "big data", "data engineering",
    "cloud computing", "software engineering", "web development", "full stack", "frontend development",
    "backend development", "mobile development", "system architecture", "microservices architecture",
    "ci/cd pipeline", "version control", "project management", "agile methodology", "scrum framework",
    "object oriented programming", "functional programming", "relational database", "nosql database",
    "rest api", "restful api", "graphql api", "distributed systems", "information security",
    "cloud native", "user interface", "user experience", "product management", "quality assurance"
]

def extract_noun_phrases(text: str) -> List[str]:
    """
    Extracts multi-word noun phrases and common tech concepts from raw text using token windows.
    """
    if not text:
        return []
        
    text_lower = text.lower()
    phrases = []
    
    # 1. Look for pre-defined tech phrases
    for phrase in COMMON_TECH_PHRASES:
        if phrase in text_lower:
            phrases.append(phrase)
            
    # 2. Extract consecutive capitalized words (names, titles, organizations)
    # E.g. "Google Cloud Platform", "San Jose State University"
    cap_phrases = re.findall(r'\b[A-Z][a-zA-Z\+\#]+\b(?:\s+[A-Z][a-zA-Z\+\#]+\b)+', text)
    for p in cap_phrases:
        if len(p.split()) > 1:
            phrases.append(p.strip())
            
    # 3. Dynamic noun-phrase heuristic: adjective/noun + noun pairs
    # E.g. "scalable service", "relational database"
    words = re.findall(r'\b[a-z]{3,}\b', text_lower)
    # Filter stop words from text preprocessor to prevent things like "in the"
    from nlp.text_preprocessor import DEFAULT_STOPWORDS
    
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i+1]
        if w1 not in DEFAULT_STOPWORDS and w2 not in DEFAULT_STOPWORDS:
            # Check common noun/adjective suffix patterns
            is_w1_adj_or_noun = (
                w1.endswith("al") or w1.endswith("ive") or w1.endswith("ic") or 
                w1.endswith("ent") or w1.endswith("able") or w1.endswith("ing") or
                w1.endswith("er") or w1.endswith("ist") or w1.endswith("tor") or
                len(w1) > 3
            )
            is_w2_noun = (
                w2.endswith("tion") or w2.endswith("ment") or w2.endswith("ity") or
                w2.endswith("nce") or w2.endswith("er") or w2.endswith("or") or
                w2.endswith("stem") or w2.endswith("base") or w2.endswith("engine") or
                w2.endswith("work") or w2.endswith("code") or w2.endswith("app")
            )
            if is_w1_adj_or_noun and is_w2_noun:
                phrases.append(f"{w1} {w2}")
                
    # Normalize and dedup (retaining case for capital phrases)
    unique_phrases = []
    seen = set()
    for p in phrases:
        norm = p.lower().strip()
        if norm not in seen and len(norm) > 5:
            seen.add(norm)
            unique_phrases.append(p)
            
    return unique_phrases
