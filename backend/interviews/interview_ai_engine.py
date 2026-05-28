import os
import logging
import asyncio
from typing import Dict, Any, List
from functools import partial
import google.generativeai as genai
from ai.response_parser import parse_ai_response

logger = logging.getLogger(__name__)
api_key = os.getenv("GEMINI_API_KEY")

class InterviewAIEngine:
    @staticmethod
    def _get_fallback_grading(question: str, user_answer: str) -> Dict[str, Any]:
        """
        Fallback grading model when Gemini API is unavailable.
        """
        answer_lower = user_answer.lower()
        score = 50
        
        positive_keywords = ["implement", "design", "manage", "scale", "optimize", "experience", "use", "project", "architecture"]
        matches = sum(1 for kw in positive_keywords if kw in answer_lower)
        score += min(35, matches * 5)
        
        if len(user_answer) > 150:
            score += 10
        score = min(100, score)
        
        confidence_score = min(100, int(score * 0.9))
        
        evaluation = "This is a reasonable attempt. Your answer covers some base concepts, but could benefit from a more structured explanation of trade-offs."
        if score >= 80:
            evaluation = "Excellent, highly detailed response. You clearly demonstrate an understanding of core concepts and design decisions."
        elif score < 60:
            evaluation = "Your response is somewhat brief. To improve, try to structure your answer using the STAR method (Situation, Task, Action, Result) and add metrics."
            
        suggestions = "Highlight metrics, quantify improvements (e.g. 'reduced latency by 20%'), and detail specific technologies."
        if "fastapi" in answer_lower or "react" in answer_lower or "docker" in answer_lower:
            suggestions = "Explain the design patterns you used. Discuss how you scaled or modularized the components."
            
        follow_up = "You mentioned key features of your stack. Can you expand on how you would secure those endpoints or design for high accessibility?"
        
        return {
            "score": score,
            "confidence_score": confidence_score,
            "ai_evaluation": evaluation,
            "improvement_suggestions": suggestions,
            "follow_up_question": follow_up
        }

    @classmethod
    async def grade_answer(
        cls,
        question: str,
        question_type: str,
        ideal_concepts: List[str],
        user_answer: str
    ) -> Dict[str, Any]:
        """
        Grades a user answer against the target question and ideal concepts.
        Outputs quality score, confidence score, feedback, suggestions, and follow-up.
        """
        fallback = cls._get_fallback_grading(question, user_answer)
        if not api_key:
            return fallback
            
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are an expert technical interviewer. Evaluate the candidate's answer against the target question and key concepts. Output strictly in the requested JSON format."
            )
            
            prompt = f"""
            Question: "{question}"
            Question Type: {question_type}
            Ideal Concepts: {ideal_concepts}
            User Answer: "{user_answer}"
            
            Please evaluate this response. Grade answer quality (score 0-100), candidate articulation confidence (confidence_score 0-100), general critique (ai_evaluation), and specific action steps (improvement_suggestions). 
            Generate an adaptive, relevant follow-up question based on their answer to challenge them further.
            
            Output strictly in this JSON format:
            {{
              "score": 85,
              "confidence_score": 90,
              "ai_evaluation": "Your critique of their response.",
              "improvement_suggestions": "Your actionable tips.",
              "follow_up_question": "A logical follow-up question."
            }}
            """
            
            loop = asyncio.get_running_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            
            if response and response.text:
                parsed = parse_ai_response(response.text, fallback)
                return {
                    "score": int(parsed.get("score", fallback["score"])),
                    "confidence_score": int(parsed.get("confidence_score", fallback["confidence_score"])),
                    "ai_evaluation": parsed.get("ai_evaluation", fallback["ai_evaluation"]),
                    "improvement_suggestions": parsed.get("improvement_suggestions", fallback["improvement_suggestions"]),
                    "follow_up_question": parsed.get("follow_up_question", fallback["follow_up_question"])
                }
                
            return fallback
        except Exception as e:
            logger.error(f"Gemini grading evaluation failed: {e}. Serving fallback.")
            return fallback
