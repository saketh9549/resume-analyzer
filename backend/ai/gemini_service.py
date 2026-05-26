import os
import logging
import asyncio
from functools import partial
import google.generativeai as genai
from ai.prompts.feedback_prompt import SYSTEM_INSTRUCTION, get_feedback_prompt
from ai.prompts.optimization_prompt import (
    SUMMARY_REWRITE_INSTRUCTION, get_summary_rewrite_prompt,
    SKILL_RECOMMENDATION_INSTRUCTION, get_skill_recommendation_prompt
)
from ai.response_parser import parse_ai_response

logger = logging.getLogger(__name__)

# Fallback structures matching Phase 4 response schema
FEEDBACK_FALLBACK = {
    "strengths": [
        "Clear baseline document layout.",
        "Demonstrates familiarity with modern programming languages."
    ],
    "weaknesses": [
        "Lack of quantified achievements (e.g., performance increases, times saved).",
        "Sparse description detail in project highlights."
    ],
    "suggestions": [
        "Revise work experience bullet points to lead with strong action verbs.",
        "Include metrics showing exact percentages of improvements in responsibilities."
    ],
    "missing_technologies": ["Docker", "Kubernetes", "Redis", "AWS"],
    "career_readiness": "Intermediate",
    "recruiter_feedback": "The candidate has a solid foundational understanding of software development. However, the resume lacks details about quantitative business impact and containerized deployment pipelines, which are critical for passing enterprise recruiter scans.",
    "project_feedback": [
        {
            "title": "Resume Analyzer",
            "feedback": "Project uses appropriate full-stack libraries, but details showing system latency or scale bounds are missing.",
            "rating": "Average"
        }
    ],
    "experience_feedback": [
        {
            "company": "Tech Corp",
            "feedback": "Bullet points are too descriptive of duties rather than outcomes. Shift focus toward deliverables.",
            "rating": "Needs Improvement"
        }
    ],
    "learning_recommendations": [
        "Learn Docker and containerization architectures.",
        "Pursue an AWS Cloud Practitioner certification to showcase cloud-native understanding."
    ]
}

REWRITE_FALLBACK = {
    "original_summary": "Original summary text",
    "suggested_summary": "Innovative Software Engineer with hands-on experience designing reactive web dashboards and secure REST API services. Passionate about automating deployment workflows, integrating intelligent parser engines, and building performance-optimized cloud architectures.",
    "key_improvements": [
        "Replaced passive descriptions with active industry action verbs.",
        "Synthesized tech stack references into key focus domains."
    ]
}

RECOMMEND_FALLBACK = {
    "recommended_skills": [
        {
            "name": "Docker",
            "reason": "Containerization is required to build replicable and scalable cloud-native architectures.",
            "difficulty": "Intermediate"
        },
        {
            "name": "Redis",
            "reason": "Used widely to configure memory caches and process rapid data queues.",
            "difficulty": "Intermediate"
        }
    ],
    "certifications": [
        "AWS Certified Developer - Associate",
        "Certified Kubernetes Administrator (CKA)"
    ],
    "learning_steps": [
        "1. Complete a foundational container course and Dockerize your local FastAPI backend.",
        "2. Study Redis basic key-value data models and integrate caching onto API routes.",
        "3. Read Kubernetes architecture guidelines to understand replica set management."
    ]
}

# Configure Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    logger.info("Gemini API client initialized successfully.")
else:
    logger.warning("GEMINI_API_KEY environment variable is missing. Running in offline/mock fallback mode.")

class GeminiAIService:
    @staticmethod
    async def analyze_resume(
        resume_data: dict, 
        model_name: str = "gemini-2.5-flash", 
        strictness: str = "standard"
    ) -> dict:
        """
        Asynchronously sends parsed resume data to Gemini to get deep recruiter feedback,
        injecting semantic guidelines from the RAG pipeline.
        """
        if not api_key:
            logger.warning("Gemini offline. Utilizing mock feedback data.")
            return FEEDBACK_FALLBACK

        try:
            prompt = get_feedback_prompt(resume_data)
            sys_inst = f"{SYSTEM_INSTRUCTION}\nStrictness Level configuration: {strictness}"
            
            # 1. RAG Context Injection
            try:
                from rag.prompt_builder import PromptBuilder
                skills_query = " ".join(resume_data.get("skills", []))
                rag_query = f"ATS resume optimization recruiter review formatting guidelines {skills_query}"
                prompt, sys_inst = await PromptBuilder.build_rag_prompt(
                    original_prompt=prompt,
                    query=rag_query,
                    system_instruction=sys_inst,
                    limit=2
                )
            except Exception as re:
                logger.error(f"Failed to compile RAG context for analyze_resume: {re}")

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=sys_inst
            )
            
            loop = asyncio.get_event_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            
            if response and response.text:
                return parse_ai_response(response.text, FEEDBACK_FALLBACK)
            
            return FEEDBACK_FALLBACK
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}. Falling back to default data.")
            return FEEDBACK_FALLBACK

    @staticmethod
    async def rewrite_summary(
        resume_data: dict,
        current_summary: str = "",
        model_name: str = "gemini-2.5-flash"
    ) -> dict:
        """
        Asynchronously rewrites summary text based on resume history details and RAG context.
        """
        if not api_key:
            return {**REWRITE_FALLBACK, "original_summary": current_summary}

        try:
            prompt = get_summary_rewrite_prompt(resume_data, current_summary)
            sys_inst = SUMMARY_REWRITE_INSTRUCTION
            
            # 2. RAG Context Injection
            try:
                from rag.prompt_builder import PromptBuilder
                skills_query = " ".join(resume_data.get("skills", []))
                rag_query = f"resume professional summary rewrite focus formatting verbs {skills_query}"
                prompt, sys_inst = await PromptBuilder.build_rag_prompt(
                    original_prompt=prompt,
                    query=rag_query,
                    system_instruction=sys_inst,
                    limit=2
                )
            except Exception as re:
                logger.error(f"Failed to compile RAG context for rewrite_summary: {re}")

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=sys_inst
            )
            
            loop = asyncio.get_event_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            
            if response and response.text:
                return parse_ai_response(response.text, REWRITE_FALLBACK)
            
            return REWRITE_FALLBACK
        except Exception as e:
            logger.error(f"Gemini summary rewrite failed: {e}")
            return {**REWRITE_FALLBACK, "original_summary": current_summary}

    @staticmethod
    async def recommend_skills(
        skills: list,
        model_name: str = "gemini-2.5-flash"
    ) -> dict:
        """
        Asynchronously maps growth learning paths based on current technical skills and RAG progression guidelines.
        """
        if not api_key:
            return RECOMMEND_FALLBACK

        try:
            prompt = get_skill_recommendation_prompt(skills)
            sys_inst = SKILL_RECOMMENDATION_INSTRUCTION
            
            # 3. RAG Context Injection
            try:
                from rag.prompt_builder import PromptBuilder
                skills_query = " ".join(skills)
                rag_query = f"skill gap progression certification roadmap devops cloud learning steps {skills_query}"
                prompt, sys_inst = await PromptBuilder.build_rag_prompt(
                    original_prompt=prompt,
                    query=rag_query,
                    system_instruction=sys_inst,
                    limit=2
                )
            except Exception as re:
                logger.error(f"Failed to compile RAG context for recommend_skills: {re}")

            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=sys_inst
            )
            
            loop = asyncio.get_event_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            
            if response and response.text:
                return parse_ai_response(response.text, RECOMMEND_FALLBACK)
            
            return RECOMMEND_FALLBACK
        except Exception as e:
            logger.error(f"Gemini skills recommendation failed: {e}")
            return RECOMMEND_FALLBACK

