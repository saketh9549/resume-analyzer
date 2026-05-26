import logging

logger = logging.getLogger(__name__)

class LayoutScorer:
    @staticmethod
    def calculate_local_layout_scores(parsed_data: dict, text: str) -> dict:
        """
        Locally analyzes resume parsed metadata to generate structural layout indices.
        Checks section presence, text density, and contact detail completeness.
        """
        scores = {}
        
        # 1. Section Completeness (Are all primary sections present?)
        required_sections = ["skills", "education", "experience", "projects"]
        present_sections = [s for s in required_sections if parsed_data.get(s)]
        scores["structure_index"] = int((len(present_sections) / len(required_sections)) * 100)
        
        # 2. Text Density Balance (Is document text too sparse or too dense?)
        char_count = len(text)
        # Optimal character count for single-page resume is between 1500 and 3500 chars
        if 1500 <= char_count <= 3500:
            density_score = 100
        elif char_count < 1000:
            density_score = max(40, int((char_count / 1500) * 100))
        else: # very dense
            density_score = max(50, 100 - int(((char_count - 3500) / 3000) * 50))
        scores["density_balance_score"] = density_score

        # 3. Contact Details Score
        contact = parsed_data.get("contact", {})
        filled_fields = [k for k, v in contact.items() if v and str(v).strip()]
        scores["contact_completeness_score"] = int((len(present_sections) / 4) * 100) # placeholder logic
        scores["contact_completeness_score"] = min(100, len(filled_fields) * 25) # e.g. email, phone, name, github/linkedin = 4 fields = 100%

        # 4. Aggregated local quality estimate
        scores["local_layout_quality"] = int(
            (scores["structure_index"] * 0.4) + 
            (scores["density_balance_score"] * 0.4) + 
            (scores["contact_completeness_score"] * 0.2)
        )
        
        return scores
