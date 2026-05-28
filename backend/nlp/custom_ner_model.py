import re
from typing import List, Dict, Any, Tuple

class CustomNERModel:
    def __init__(self):
        # List of regex rules representing entity types
        self.rules = [
            # Degree types
            (r'\b(bachelor|master|ph\.?d|b\.?s|m\.?s|b\.?tech|m\.?tech|m\.?b\.?a|associate|degree)\b', "DEGREE"),
            # Common programming languages
            (r'\b(python|javascript|typescript|java|c\+\+|c\#|golang|go|rust|ruby|php|html|css)\b', "PROGRAMMING_LANGUAGE"),
            # Common frameworks
            (r'\b(react|angular|vue|next\.js|node\.js|express|fastapi|django|flask|spring boot)\b', "FRAMEWORK"),
            # Cloud
            (r'\b(aws|azure|gcp|docker|kubernetes|terraform)\b', "CLOUD_PLATFORM"),
            # Common databases
            (r'\b(postgresql|postgres|mysql|mongodb|redis|sqlite)\b', "DATABASE"),
            # Years of experience patterns
            (r'\b(\d+)\+?\s*(?:years?|yrs?)\s+of\s+experience\b', "YEARS_EXPERIENCE"),
            (r'\bexperience\s*:\s*(\d+)\+?\s*years?\b', "YEARS_EXPERIENCE")
        ]

    def predict(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans text and returns predicted entity segments with labels, offsets, and confidence scores.
        """
        entities = []
        text_lower = text.lower()
        
        for pattern, label in self.rules:
            for match in re.finditer(pattern, text_lower):
                start, end = match.span()
                matched_text = text[start:end]
                
                # Confidence is higher for specific matches
                confidence = 0.95
                if label == "YEARS_EXPERIENCE":
                    confidence = 0.98
                    # extract the number of years from match
                    num_match = re.search(r'\d+', matched_text)
                    val = num_match.group(0) if num_match else matched_text
                else:
                    val = matched_text
                    
                entities.append({
                    "text": val,
                    "label": label,
                    "start": start,
                    "end": end,
                    "confidence": confidence
                })
                
        # Remove overlaps (keep longer span or higher confidence)
        entities = sorted(entities, key=lambda x: (x["end"] - x["start"]), reverse=True)
        filtered = []
        seen_spans = set()
        
        for ent in entities:
            span_range = range(ent["start"], ent["end"])
            overlap = False
            for span in seen_spans:
                if ent["start"] in span or ent["end"] - 1 in span:
                    overlap = True
                    break
            if not overlap:
                filtered.append(ent)
                seen_spans.add(span_range)
                
        return sorted(filtered, key=lambda x: x["start"])
