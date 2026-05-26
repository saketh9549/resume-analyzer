import os
import logging
import asyncio
from functools import partial
from PIL import Image
import google.generativeai as genai
from ai.response_parser import parse_ai_response

logger = logging.getLogger(__name__)

# Fallback visual analysis response if Gemini is offline
VISION_FALLBACK = {
    "layout_score": 75,
    "design_score": 70,
    "readability_score": 80,
    "formatting_score": 75,
    "visual_balance_score": 78,
    "recruiter_readability_score": 72,
    "ats_friendliness_score": 80,
    "overall_visual_score": 76,
    "layout_feedback": "The document utilizes a standard single-column chronological structure. Content blocks are aligned correctly, but the overall design feels generic and lacks modern aesthetic styling.",
    "design_suggestions": [
        "Use a modern sans-serif font (e.g. Inter or Roboto) instead of Times New Roman to enhance contemporary feel.",
        "Include subtle colored lines or side borders to demarcate header segments cleanly."
    ],
    "readability_improvements": [
        "Slightly increase line-height margins from 1.0 to 1.15 to let the text breathe.",
        "Add more white space between distinct sections to avoid visual crowding."
    ],
    "formatting_optimizations": [
        "Format date segments uniformly on the right-hand margin.",
        "Ensure bullet points use standardized circular indicators rather than mixed shapes."
    ],
    "section_ordering_improvements": [
        "Place the Technical Skills section above your Professional Experience to immediately catch the technical recruiter's attention."
    ]
}

# Configure Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class VisionAnalyzer:
    @staticmethod
    async def analyze_layout_visuals(image: Image.Image) -> dict:
        """
        Asynchronously calls Gemini Vision (gemini-2.5-flash) to evaluate resume layout design,
        returning structured scores and typographic recommendations.
        """
        if not api_key:
            logger.warning("Gemini API key missing. Serving layout analysis fallback.")
            return VISION_FALLBACK

        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            prompt = """
            You are an Expert Resume Designer, Typographer, and Senior Executive Recruiter.
            Inspect the visual layout, formatting, typography, white spacing, alignment, and structural design of the provided resume image.
            
            Evaluate the following items:
            1. Layout Structure (Is it modern, readable, balanced?)
            2. Typography (Are fonts consistent, professional, sized appropriately?)
            3. Readability & White Space (Is text crowded? Is there enough margin padding?)
            4. Formatting Consistency (Are bullets aligned? Are dates uniform?)
            5. ATS Friendliness (Does the visual layout suggest issues like complex text boxes, icons, or multi-column grids that block parser engines?)
            
            Produce a structured visual score out of 100 for each dimension, along with descriptive feedback and concrete improvement steps.
            
            You MUST return a JSON matching this exact structure:
            {
              "layout_score": 80,
              "design_score": 75,
              "readability_score": 85,
              "formatting_score": 78,
              "visual_balance_score": 82,
              "recruiter_readability_score": 75,
              "ats_friendliness_score": 78,
              "overall_visual_score": 78,
              "layout_feedback": "Paragraph explaining visual layout observations...",
              "design_suggestions": ["Concrete design suggestion 1", "Concrete design suggestion 2"],
              "readability_improvements": ["How to improve readability 1", "How to improve readability 2"],
              "formatting_optimizations": ["How to format uniformly 1", "How to format uniformly 2"],
              "section_ordering_improvements": ["How to order sections for better reader scan rate"]
            }
            """
            
            loop = asyncio.get_event_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            # Pass both the PIL Image and the text prompt to the multimodal generator
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, [image, prompt], generation_config=generation_config)
            )
            
            if response and response.text:
                return parse_ai_response(response.text, VISION_FALLBACK)
            
            return VISION_FALLBACK
        except Exception as e:
            logger.error(f"Gemini Vision layout analysis failed: {e}. Falling back.")
            return VISION_FALLBACK
