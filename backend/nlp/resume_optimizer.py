import os
import logging
import asyncio
from functools import partial
import google.generativeai as genai
from nlp.rewrite_recommendations import REWRITE_PAIRS

logger = logging.getLogger(__name__)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class ResumeOptimizer:
    @classmethod
    async def optimize_bullet_point(cls, bullet_point: str, focus_area: str = "ATS Optimization") -> str:
        """
        Uses Gemini to rewrite a passive experience statement into a metric-rich, action-oriented bullet point.
        """
        clean_bullet = bullet_point.strip()
        if not clean_bullet:
            return ""
            
        # 1. Look for pre-defined template mapping first
        for pair in REWRITE_PAIRS:
            if pair["phrase"] in clean_bullet.lower():
                return pair["suggestion"]
                
        # 2. Query Gemini if configured
        if api_key:
            try:
                prompt = (
                    f"You are a professional executive resume writer.\n"
                    f"Rewrite the following passive resume statement to make it action-oriented, "
                    f"ATS-friendly, and show quantified metrics. Focus area: {focus_area}.\n\n"
                    f"Original: \"{clean_bullet}\"\n\n"
                    f"Return ONLY the rewritten sentence, with no quotes, preamble, or conversational notes."
                )
                
                loop = asyncio.get_running_loop()
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                response = await loop.run_in_executor(
                    None,
                    partial(
                        model.generate_content,
                        prompt
                    )
                )
                if response and response.text:
                    return response.text.strip().replace('"', '')
            except Exception as e:
                logger.error(f"Gemini resume optimization failed: {e}")
                
        # 3. Dynamic Rule Fallback
        # If the bullet is extremely short, expand it with a template
        words = clean_bullet.split()
        if len(words) < 5:
            return f"Spearheaded and developed {clean_bullet} systems, achieving a 20% increase in operational efficiency."
            
        # Add active verb and metric suffix
        from nlp.action_verb_analyzer import STRONG_ACTION_VERBS
        import random
        verb = random.choice(list(STRONG_ACTION_VERBS))
        
        return f"{verb.capitalize()} and optimized key components to {clean_bullet.lower()}, boosting overall processing velocity by 25%."
