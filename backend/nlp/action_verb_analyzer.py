import re
from typing import Dict, Any, List

# List of weak verbs and their corresponding strong recommendations
WEAK_TO_STRONG_VERBS = {
    "helped": ["spearheaded", "supported", "collaborated on", "facilitated"],
    "worked": ["engineered", "implemented", "driven", "orchestrated", "architected"],
    "involved": ["led", "managed", "coordinated", "steered", "directed"],
    "assisted": ["partnered", "sustained", "bolstered", "executed"],
    "did": ["accomplished", "engineered", "completed", "executed"],
    "made": ["created", "formulated", "authored", "constructed", "engineered"],
    "took": ["assumed", "commanded", "steered", "championed"],
    "used": ["leveraged", "utilized", "deployed", "implemented", "harnessed"],
    "managed": ["spearheaded", "directed", "coordinated", "steered"],
    "responsible": ["spearheaded", "owned", "executed", "oversaw"]
}

STRONG_ACTION_VERBS = {
    "engineered", "optimized", "architected", "developed", "formulated", "spearheaded",
    "designed", "automated", "orchestrated", "implemented", "accelerated", "maximized",
    "modernized", "redesigned", "pioneered", "steered", "overhauled", "cultivated",
    "enhanced", "boosted", "delivered", "executed", "coordinated", "resolved", "decreased"
}

def analyze_experience_verbs(responsibilities: List[str]) -> Dict[str, Any]:
    """
    Analyzes action verb strength in the bullet points of a resume experience section.
    
    Returns:
        Dict: weak_verbs found, strong_verbs found, suggestions list, and verb_score.
    """
    weak_found = []
    strong_found = []
    suggestions = []
    
    total_bullets = len(responsibilities)
    if total_bullets == 0:
        return {
            "weak_verbs": [],
            "strong_verbs": [],
            "suggestions": [],
            "verb_score": 100
        }
        
    for bullet in responsibilities:
        words = re.findall(r'\b[a-zA-Z]+\b', bullet.lower())
        
        # Check first word in the bullet point (usually the action verb)
        if words:
            first_word = words[0]
            
            # Simple POS check fallback (stem to past/present root)
            from nlp.text_preprocessor import lemmatize_word
            first_lemma = lemmatize_word(first_word)
            
            if first_lemma in WEAK_TO_STRONG_VERBS or first_word in WEAK_TO_STRONG_VERBS:
                weak_match = first_lemma if first_lemma in WEAK_TO_STRONG_VERBS else first_word
                weak_found.append({
                    "verb": first_word,
                    "sentence": bullet,
                    "replacements": WEAK_TO_STRONG_VERBS[weak_match]
                })
                suggestions.append(
                    f"Replace weak leading verb '{first_word}' in bullet point with: {', '.join(WEAK_TO_STRONG_VERBS[weak_match][:3])}."
                )
            elif first_word in STRONG_ACTION_VERBS or first_lemma in STRONG_ACTION_VERBS:
                strong_found.append(first_word)
                
        # Also scan the rest of the sentence for other weak patterns
        for word in words[1:]:
            if word in WEAK_TO_STRONG_VERBS:
                weak_found.append({
                    "verb": word,
                    "sentence": bullet,
                    "replacements": WEAK_TO_STRONG_VERBS[word]
                })
                
    # Calculate score based on ratio of strong verbs to weak verbs and bullets analyzed
    total_weak = len(weak_found)
    total_strong = len(strong_found)
    
    # Base score of 80, add points for strong verbs, subtract for weak verbs
    raw_score = 80 + (total_strong * 10) - (total_weak * 15)
    verb_score = max(20, min(100, raw_score))
    
    return {
        "weak_verbs": weak_found,
        "strong_verbs": list(set(strong_found)),
        "suggestions": list(set(suggestions))[:4],
        "verb_score": int(verb_score)
    }
