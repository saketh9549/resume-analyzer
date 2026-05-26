import os
import logging
import asyncio
from typing import List, Dict, Any
from functools import partial
import google.generativeai as genai
from ai.response_parser import parse_ai_response

logger = logging.getLogger(__name__)

# Fallbacks for offline execution modes
CAREER_FALLBACK = {
    "career_summary": "Based on your technical background, you demonstrate solid capabilities in software construction and backend APIs. Transitioning towards DevOps or Cloud architectures would offer strong market upside.",
    "recommended_tracks": [
      {
        "role": "Backend Engineer",
        "alignment_reason": "Strong alignment with core languages and databases detailed in your projects.",
        "difficulty": "Easy (Ready to apply)",
        "salary_upside": "High"
      },
      {
        "role": "DevOps Engineer",
        "alignment_reason": "High interest but missing container clustering and deployment setups in current bullets.",
        "difficulty": "Medium (Requires learning Kubernetes & CI/CD)",
        "salary_upside": "Very High"
      }
    ],
    "overall_guidance": "To reach high-paying Senior roles, focus on container orchestrations, cloud hosting providers, and system design patterns.",
    "transition_advice": "Start by containerizing your current projects and adding cloud certificates to build architectural credibility."
}

ROADMAP_FALLBACK = {
    "roadmap_steps": [
        {
            "step": 1,
            "topic": "Containerization Fundamentals",
            "description": "Understand microservice packaging using Docker. Build Dockerfiles and docker-compose orchestration environments locally.",
            "recommended_courses_or_resources": ["Docker & Kubernetes Course on Udemy", "Official Docker Documentation Guide"],
            "timeline": "2 Weeks"
        },
        {
            "step": 2,
            "topic": "CI/CD Integration Pipelines",
            "description": "Configure automated verification checks. Integrate static lints, unittests, and auto-build operations with GitHub Actions.",
            "recommended_courses_or_resources": ["GitHub Actions tutorial series", "DevOps Roadmap site guides"],
            "timeline": "3 Weeks"
        },
        {
            "step": 3,
            "topic": "Cloud Deployment & Infrastructure",
            "description": "Deploy backend applications onto AWS using ECS or EKS. Practice basic security group rules and scaling configurations.",
            "recommended_courses_or_resources": ["AWS Developer Associate certifications path"],
            "timeline": "4 Weeks"
        }
    ],
    "certification_suggestions": [
        "AWS Certified Developer - Associate",
        "HashiCorp Certified Terraform Associate"
    ],
    "priority_skills": ["Docker", "Kubernetes", "AWS ECS", "GitHub Actions"]
}

# Configure Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class JobRecommendationEngine:
    @staticmethod
    async def generate_career_guidance(resume_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calls Gemini to generate custom career advice and transition insights.
        """
        if not api_key:
            logger.warning("Gemini offline. Utilizing mock career recommendations.")
            return CAREER_FALLBACK

        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are a Principal Career Advisor and Tech Recruiter. You must analyze the candidate's parsed resume details and preferred settings to output career guidance in strict JSON format."
            )
            
            prompt = f"""
            Parsed Candidate Resume:
            Skills: {resume_data.get('skills', [])}
            Projects: {[{'name': p.get('name'), 'technologies': p.get('technologies')} for p in resume_data.get('projects', [])]}
            Experience: {[{'job_title': e.get('job_title'), 'duration': e.get('duration')} for e in resume_data.get('experience', [])]}
            ATS Score: {resume_data.get('ats_score', 0)}
            
            Preferred User settings:
            {preferences or {}}
            
            Generate custom guidance in this JSON schema:
            {{
              "career_summary": "text summarizing candidate position",
              "recommended_tracks": [
                {{
                  "role": "job role title",
                  "alignment_reason": "why they match or what makes this path interesting",
                  "difficulty": "Easy / Medium / Hard estimation",
                  "salary_upside": "Moderate / High / Very High"
                }}
              ],
              "overall_guidance": "actionable overarching career tips",
              "transition_advice": "tactical steps to enter these recommended roles"
            }}
            """
            
            loop = asyncio.get_event_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            
            if response and response.text:
                return parse_ai_response(response.text, CAREER_FALLBACK)
            
            return CAREER_FALLBACK
        except Exception as e:
            logger.error(f"Gemini career advice failure: {e}")
            return CAREER_FALLBACK

    @staticmethod
    async def generate_learning_roadmap(
        job_title: str,
        missing_skills: List[str],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calls Gemini to create a sequential study roadmap to fill gaps for a specific job.
        """
        if not api_key:
            logger.warning("Gemini offline. Utilizing mock learning roadmap.")
            return ROADMAP_FALLBACK

        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are an expert Technical Coach. Create a detailed study roadmap to bridge the gap between a candidate's resume and a target job. Output in strict JSON format."
            )
            
            prompt = f"""
            Target Job Title: {job_title}
            Missing Skills detected: {missing_skills}
            Current Candidate Skills: {resume_data.get('skills', [])}
            
            Create a step-by-step learning roadmap in this JSON schema:
            {{
              "roadmap_steps": [
                {{
                  "step": 1,
                  "topic": "topic name to study",
                  "description": "what specific frameworks, architectures or concepts to learn",
                  "recommended_courses_or_resources": ["Udemy course name, YouTube channel or official docs"],
                  "timeline": "timeframe e.g. '2 Weeks'"
                }}
              ],
              "certification_suggestions": ["industry standard certs to take"],
              "priority_skills": ["top 3-4 technologies they must learn first"]
            }}
            """
            
            loop = asyncio.get_event_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            
            if response and response.text:
                return parse_ai_response(response.text, ROADMAP_FALLBACK)
            
            return ROADMAP_FALLBACK
        except Exception as e:
            logger.error(f"Gemini learning roadmap failure: {e}")
            return ROADMAP_FALLBACK
