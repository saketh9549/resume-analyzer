import os
import json
import logging
import asyncio
from typing import Dict, Any, List
from functools import partial
import google.generativeai as genai
from ai.response_parser import parse_ai_response

logger = logging.getLogger(__name__)
api_key = os.getenv("GEMINI_API_KEY")

class ResumeQuestionGenerator:
    @staticmethod
    def _get_mock_fallback_questions(
        job_title: str,
        difficulty: str,
        mode: str,
        skills: List[str],
        experience: List[Dict[str, Any]],
        projects: List[Dict[str, Any]],
        ats_weaknesses: List[str]
    ) -> List[Dict[str, Any]]:
        """
        High-fidelity local fallback question generator in case Gemini is offline or fails.
        Creates questions highly relevant to the candidate's exact experience/skills.
        """
        # Determine candidate skills/company defaults
        skill_1 = skills[0] if len(skills) > 0 else "Python"
        skill_2 = skills[1] if len(skills) > 1 else "FastAPI"
        skill_3 = skills[2] if len(skills) > 2 else "React"
        
        company = experience[0].get("company", "your previous company") if experience else "your previous job"
        role_title = experience[0].get("job_title", "Software Engineer") if experience else "Software Engineer"
        project_name = projects[0].get("name", "Resume Analyzer") if projects else "Resume Analyzer"
        weakness = ats_weaknesses[0] if ats_weaknesses else "System Scaling"
        
        questions = []
        
        if mode.lower() in ["technical", "technical"]:
            questions = [
                {
                    "question": f"Explain the architectural patterns and design choices you made when working with {skill_1} and {skill_2}.",
                    "question_type": "technical",
                    "ideal_concepts": [skill_1.lower(), skill_2.lower(), "architecture", "design pattern"]
                },
                {
                    "question": f"How do you configure and optimize database operations (like indexes in MongoDB or PostgreSQL) when using {skill_2}?",
                    "question_type": "technical",
                    "ideal_concepts": ["indexing", "optimization", "database", skill_2.lower()]
                },
                {
                    "question": f"Detail how you would approach testing, validation, and debugging for a system built on {skill_1}.",
                    "question_type": "technical",
                    "ideal_concepts": ["unit testing", "debugging", "pytest", "mocking"]
                },
                {
                    "question": f"Your resume mentions {skill_3}. How do you handle state management, lifecycle hooks, and page rendering optimization?",
                    "question_type": "technical",
                    "ideal_concepts": [skill_3.lower(), "state", "optimization", "rendering"]
                },
                {
                    "question": f"How do you address the missing skill '{weakness}' mentioned in your profiles or general system design?",
                    "question_type": "technical",
                    "ideal_concepts": [weakness.lower(), "mitigation", "best practices"]
                }
            ]
        elif mode.lower() == "behavioral":
            questions = [
                {
                    "question": f"Describe a situation at {company} where you acted as a lead or took initiative on a major feature. What was the outcome?",
                    "question_type": "behavioral",
                    "ideal_concepts": ["initiative", "leadership", "impact", "star method"]
                },
                {
                    "question": "Tell me about a time you had a technical disagreement with a team member. How did you coordinate to find a solution?",
                    "question_type": "behavioral",
                    "ideal_concepts": ["conflict resolution", "collaboration", "communication"]
                },
                {
                    "question": f"While working as a {role_title}, how did you manage project scope shifts under tight deadline constraints?",
                    "question_type": "behavioral",
                    "ideal_concepts": ["prioritization", "scoping", "time management"]
                },
                {
                    "question": "Describe a failure you experienced in a project. What did you learn, and how did you apply that lesson subsequently?",
                    "question_type": "behavioral",
                    "ideal_concepts": ["failure", "reflection", "learning", "growth"]
                },
                {
                    "question": "How do you maintain focus and structure when working on complex, ambiguous customer requirements?",
                    "question_type": "behavioral",
                    "ideal_concepts": ["ambiguity", "structure", "problem solving"]
                }
            ]
        elif mode.lower() == "hr":
            questions = [
                {
                    "question": f"Why are you looking to join as a {job_title}? How do your skills in {skill_1} align with our open goals?",
                    "question_type": "hr",
                    "ideal_concepts": ["alignment", "interest", "skills match"]
                },
                {
                    "question": f"Reflecting on your journey from {company}, what are your career aspirations for the next 2-3 years?",
                    "question_type": "hr",
                    "ideal_concepts": ["goals", "growth", "aspirations"]
                },
                {
                    "question": "Describe your ideal working culture. Do you prefer fully remote flexibility or hybrid, collaborative models?",
                    "question_type": "hr",
                    "ideal_concepts": ["culture fit", "remote", "collaboration"]
                },
                {
                    "question": "How do you stay up-to-date with new technologies and industry frameworks? Share a recent topic you researched.",
                    "question_type": "hr",
                    "ideal_concepts": ["learning", "industry trends", "curiosity"]
                },
                {
                    "question": "What is the most rewarding feedback you have received from a manager or team member?",
                    "question_type": "hr",
                    "ideal_concepts": ["feedback", "strengths", "teamwork"]
                }
            ]
        elif mode.lower() in ["system_design", "system design"]:
            questions = [
                {
                    "question": f"How would you design a high-throughput pipeline to parse files like '{project_name}' while maintaining security and low latency?",
                    "question_type": "system_design",
                    "ideal_concepts": ["queues", "scalability", "load balancing", "caching"]
                },
                {
                    "question": f"Design a state management and storage layout for a platform using {skill_2} and MongoDB. Discuss scaling strategies.",
                    "question_type": "system_design",
                    "ideal_concepts": ["sharding", "replication", "indexing", "nosql schemas"]
                },
                {
                    "question": "Explain how you would build a rate limiter and firewall to secure API endpoints from denial-of-service threats.",
                    "question_type": "system_design",
                    "ideal_concepts": ["rate limiting", "security", "token bucket", "redis"]
                },
                {
                    "question": f"How would you architect a disaster recovery strategy if a cloud database hosting {skill_1} services goes offline?",
                    "question_type": "system_design",
                    "ideal_concepts": ["backups", "multi-region", "failover", "availability"]
                },
                {
                    "question": "How do you evaluate microservices vs. monolithic patterns? Discuss cost, developer speed, and maintainability trade-offs.",
                    "question_type": "system_design",
                    "ideal_concepts": ["microservices", "monolith", "trade-offs", "communication protocols"]
                }
            ]
        else: # project_deep_dive or default
            questions = [
                {
                    "question": f"In your project '{project_name}', walk me through the end-to-end data flow. What was your primary responsibility?",
                    "question_type": "project_deep_dive",
                    "ideal_concepts": ["data flow", "ownership", "architecture"]
                },
                {
                    "question": f"What was the most challenging technical roadblock you encountered in '{project_name}'? How did you debug it?",
                    "question_type": "project_deep_dive",
                    "ideal_concepts": ["debugging", "blocker", "problem solving"]
                },
                {
                    "question": f"If you had to rewrite '{project_name}' from scratch today with unlimited resources, what changes would you make?",
                    "question_type": "project_deep_dive",
                    "ideal_concepts": ["redesign", "lessons learned", "modern stack"]
                },
                {
                    "question": f"How did you ensure security, user access control, and data privacy inside '{project_name}'?",
                    "question_type": "project_deep_dive",
                    "ideal_concepts": ["security", "access control", "privacy"]
                },
                {
                    "question": f"How did you measure the success, speed, or optimization achievements of '{project_name}'?",
                    "question_type": "project_deep_dive",
                    "ideal_concepts": ["metrics", "optimization", "performance"]
                }
            ]
            
        return questions

    @classmethod
    async def generate_questions(
        cls,
        job_title: str,
        difficulty: str,
        mode: str,
        context_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generates 5 personalized interview questions by invoking Gemini, 
        falling back to local templates if API keys are missing or requests fail.
        """
        skills = context_data.get("skills", [])
        experience = context_data.get("experience", [])
        projects = context_data.get("projects", [])
        ats_weaknesses = context_data.get("ats_weaknesses", [])
        prompt_context = context_data.get("prompt_context", "")
        
        fallback = cls._get_mock_fallback_questions(
            job_title, difficulty, mode, skills, experience, projects, ats_weaknesses
        )
        
        if not api_key:
            logger.info("GEMINI_API_KEY not found. Serving high-fidelity local mock questions.")
            return fallback
            
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction="You are an expert Hiring Manager and Senior Recruiter. Generate highly personalized mock interview questions tailored directly to the candidate's experience, project list, technologies, and ATS weaknesses. Output strictly matching the requested JSON format."
            )
            
            prompt = f"""
            Target Job Title: {job_title}
            Interview Mode: {mode} (Technical, Behavioral, HR, System Design, Project Deep Dive)
            Difficulty Grade: {difficulty}
            
            Candidate Context:
            {prompt_context}
            
            Please analyze the candidate's skills, frameworks, projects, achievements, and ATS weaknesses. 
            Generate exactly 5 realistic, high-quality interview questions matching the specified Interview Mode.
            Ensure some questions directly address their ATS weaknesses or challenge them to defend a project choice.
            
            Output strictly in this JSON format:
            {{
              "questions": [
                {{
                  "question": "Question text here",
                  "question_type": "technical | behavioral | hr | system_design | project_deep_dive",
                  "ideal_concepts": ["concept 1", "concept 2", "concept 3"]
                }}
              ]
            }}
            """
            
            loop = asyncio.get_running_loop()
            generation_config = {"response_mime_type": "application/json"}
            
            response = await loop.run_in_executor(
                None,
                partial(model.generate_content, prompt, generation_config=generation_config)
            )
            
            if response and response.text:
                parsed = parse_ai_response(response.text, {"questions": fallback})
                questions = parsed.get("questions", fallback)
                return questions
                
            return fallback
        except Exception as e:
            logger.error(f"Gemini mock interview generation failed: {e}. Falling back to templates.")
            return fallback
