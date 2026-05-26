import json
import re
import logging

logger = logging.getLogger(__name__)

def clean_gemini_json_string(raw_text: str) -> str:
    """
    Cleans markdown code fences and extraneous text from Gemini's response.
    """
    if not raw_text:
        return ""
    
    cleaned = raw_text.strip()
    
    # Strip markdown block indicators if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    
    # In case of leading/trailing explanation text, grab content within first '{' and last '}'
    if not (cleaned.startswith("{") and cleaned.endswith("}")):
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            cleaned = match.group(1)
            
    return cleaned

def parse_ai_response(raw_text: str, fallback_template: dict) -> dict:
    """
    Parses a Gemini response string into a structured dictionary.
    Falls back gracefully if the response is invalid JSON.
    """
    cleaned = clean_gemini_json_string(raw_text)
    if not cleaned:
        logger.warning("Empty response received from AI model. Utilizing fallback template.")
        return fallback_template

    try:
        data = json.loads(cleaned)
        
        # Ensure all key properties from fallback template are present in parsed data
        for key, default_val in fallback_template.items():
            if key not in data:
                data[key] = default_val
            elif isinstance(default_val, list) and not isinstance(data[key], list):
                # Auto-correct type if a list field got returned as a non-list
                data[key] = [data[key]] if data[key] else []
                
        return data
    except Exception as e:
        logger.error(f"Failed to parse AI JSON response: {e}. Raw: {raw_text}")
        return fallback_template
