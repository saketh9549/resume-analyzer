import re
import logging
from typing import List, Dict, Any
from nlp.custom_ner_model import CustomNERModel
from nlp.skill_entity_mapper import canonicalize_entity

logger = logging.getLogger(__name__)

# Predefined vocabularies for lookups
UNIVERSITIES_VOCAB = ["stanford", "harvard", "mit", "oxford", "cambridge", "caltech", "berkeley", "cmu", "snu", "iit", "bits"]
COMPANIES_VOCAB = ["google", "microsoft", "amazon", "apple", "netflix", "meta", "facebook", "twitter", "uber", "airbnb", "stripe"]
LOCATIONS_VOCAB = ["san francisco", "new york", "london", "bangalore", "delhi", "remote", "california", "india", "boston"]
ROLES_VOCAB = ["software engineer", "developer", "backend engineer", "frontend engineer", "full stack developer", "product manager", "data scientist", "system architect", "solutions architect", "devops engineer", "intern"]
CERTIFICATIONS_VOCAB = ["aws certified", "pmp", "csm", "scrum master", "comptia", "cissp", "ccna", "gcp professional"]
TOOLS_VOCAB = ["git", "jenkins", "jira", "docker", "kubernetes", "ansible", "terraform", "webpack", "babel", "vite"]
TECHNOLOGIES_VOCAB = ["rest api", "graphql", "microservices", "ci/cd", "sql", "nosql", "machine learning", "deep learning", "nlp", "computer vision"]

class EntityExtractor:
    def __init__(self):
        self.ner_model = CustomNERModel()
        
    def extract_all_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Orchestrates extraction of 14 target entity types from a resume text.
        
        Returns:
            Dict: mapped list of entities under the 14 category keys, each entity 
                  containing the text value and confidence score.
        """
        raw_preds = self.ner_model.predict(text)
        text_lower = text.lower()
        
        # Initialize 14 category lists
        extracted: Dict[str, List[Dict[str, Any]]] = {
            "skills": [],
            "companies": [],
            "universities": [],
            "degrees": [],
            "certifications": [],
            "programming_languages": [],
            "frameworks": [],
            "cloud_platforms": [],
            "years_of_experience": [],
            "locations": [],
            "roles_titles": [],
            "achievements": [],
            "technologies": [],
            "tools": []
        }
        
        # Helper to avoid duplicates within a category
        def add_unique(category: str, value: str, confidence: float):
            canonical = canonicalize_entity(value)
            if not canonical:
                return
            for item in extracted[category]:
                if item["value"].lower() == canonical.lower():
                    # Update to higher confidence if found
                    item["confidence"] = max(item["confidence"], confidence)
                    return
            extracted[category].append({
                "value": canonical,
                "confidence": round(confidence, 2)
            })

        # 1. Map predictions from CustomNERModel first
        for pred in raw_preds:
            label = pred["label"]
            val = pred["text"]
            conf = pred["confidence"]
            
            if label == "DEGREE":
                add_unique("degrees", val.capitalize(), conf)
            elif label == "PROGRAMMING_LANGUAGE":
                add_unique("programming_languages", val, conf)
                add_unique("skills", val, conf)
            elif label == "FRAMEWORK":
                add_unique("frameworks", val, conf)
                add_unique("skills", val, conf)
            elif label == "CLOUD_PLATFORM":
                add_unique("cloud_platforms", val, conf)
                add_unique("skills", val, conf)
            elif label == "DATABASE":
                add_unique("skills", val, conf)
                add_unique("technologies", val, conf)
            elif label == "YEARS_EXPERIENCE":
                # Convert years to structured number
                add_unique("years_of_experience", f"{val} Years", conf)

        # 2. Heuristic word patterns matching for other categories
        # Companies
        for comp in COMPANIES_VOCAB:
            if re.search(r'\b' + re.escape(comp) + r'\b', text_lower):
                add_unique("companies", comp.capitalize(), 0.90)
                
        # Universities
        for univ in UNIVERSITIES_VOCAB:
            if re.search(r'\b' + re.escape(univ) + r'\b', text_lower):
                add_unique("universities", univ.upper() if len(univ) < 4 else univ.capitalize(), 0.90)
                
        # Locations
        for loc in LOCATIONS_VOCAB:
            if re.search(r'\b' + re.escape(loc) + r'\b', text_lower):
                add_unique("locations", loc.capitalize(), 0.85)
                
        # Roles/Titles
        for role in ROLES_VOCAB:
            if re.search(r'\b' + re.escape(role) + r'\b', text_lower):
                add_unique("roles_titles", role.title(), 0.92)
                
        # Certifications (from vocab or regex)
        for cert in CERTIFICATIONS_VOCAB:
            if re.search(r'\b' + re.escape(cert) + r'\b', text_lower):
                add_unique("certifications", cert.upper() if len(cert) < 4 else cert.title(), 0.95)
        # Regex search for "Certified [X]"
        certs_found = re.findall(r'\bcertified\s+([a-zA-Z0-9\+\#\s]{2,20})\b', text_lower)
        for cf in certs_found:
            add_unique("certifications", f"Certified {cf.title()}", 0.85)

        # Tools
        for tool in TOOLS_VOCAB:
            if re.search(r'\b' + re.escape(tool) + r'\b', text_lower):
                add_unique("tools", tool.capitalize() if tool not in ["git"] else tool.title(), 0.90)
                add_unique("skills", tool, 0.80)

        # Technologies
        for tech in TECHNOLOGIES_VOCAB:
            if re.search(r'\b' + re.escape(tech) + r'\b', text_lower):
                add_unique("technologies", tech.title(), 0.88)
                add_unique("skills", tech, 0.80)

        # Achievements
        # Identify sentences containing dollar signs, percent signs, numbers + metrics
        sentences = re.split(r'[\.\!\?]', text)
        for sent in sentences:
            sent_clean = sent.strip()
            if not sent_clean:
                continue
            # Look for achievement keywords (e.g. key performance indicators, increased, saved, optimized, spearhead)
            has_metric = re.search(r'\b(?:\d+%\s*(?:increase|reduction|growth|improvement)|[\$\d,]+\s*(?:saved|generated|revenue)|optimized|spearheaded|pioneered)\b', sent_clean, re.I)
            if has_metric and len(sent_clean.split()) < 25:
                # Truncate clean string
                add_unique("achievements", sent_clean, 0.85)

        # Ensure years of experience fallback by parsing experience blocks if still empty
        if not extracted["years_of_experience"]:
            # Basic sum of durations fallback
            from jobs.scoring_engine import ScoringEngine
            # Simple count years heuristic from text
            year_pattern = r'\b(19\d{2}|20[0-2]\d)\b'
            years = [int(y) for y in re.findall(year_pattern, text_lower)]
            if len(years) >= 2:
                diff = max(1, abs(years[-1] - years[0]))
                add_unique("years_of_experience", f"{diff} Years", 0.70)
            else:
                add_unique("years_of_experience", "2 Years", 0.50) # default fallback

        return extracted
