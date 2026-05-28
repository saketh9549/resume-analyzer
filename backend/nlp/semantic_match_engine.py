import logging
from typing import Dict, Any, List
from nlp.embedding_similarity import calculate_semantic_similarity
from nlp.skill_mapper import extract_matched_synonyms, check_contextual_match
from nlp.tfidf_engine import compute_tfidf_overlap

logger = logging.getLogger(__name__)

class SemanticMatchEngine:
    @classmethod
    async def match_resume_to_job(
        cls,
        resume_data: Dict[str, Any],
        job_details: Dict[str, Any],
        raw_text: str = ""
    ) -> Dict[str, Any]:
        """
        Runs semantic matching between a candidate's resume and a target job description.
        
        Returns:
            Dict: containing semantic_similarity_score, keyword_score, 
                  contextual_relevance_score, recruiter_relevance_score, 
                  and the overall aggregated score.
        """
        user_skills = resume_data.get("skills", [])
        req_skills = job_details.get("required_skills", [])
        
        job_title = job_details.get("job_title", "")
        job_desc = job_details.get("description", "")
        
        # 1. KEYWORD SCORE (Based on exact matching + synonyms)
        matched_skills = extract_matched_synonyms(user_skills, req_skills)
        if req_skills:
            keyword_score = float(len(matched_skills) / len(req_skills) * 100.0)
        else:
            keyword_score = 100.0
            
        keyword_score = round(min(100.0, keyword_score), 1)
        
        # 2. SEMANTIC SIMILARITY SCORE (Based on sentence transformer embedding cosine similarity)
        # Prepare text representation for embedding comparison
        resume_summary = " ".join([
            resume_data.get("contact", {}).get("email", ""),
            " ".join(user_skills),
            " ".join([f"{e.get('job_title', '')} {e.get('company', '')} {' '.join(e.get('responsibilities', []))}" for e in resume_data.get("experience", [])]),
            " ".join([f"{p.get('name', '')} {p.get('description', '')}" for p in resume_data.get("projects", [])])
        ])
        
        # Aggregate job targets
        job_targets = f"{job_title}. {job_desc}. Core requirements: {' '.join(req_skills)}."
        
        embedding_score = await calculate_semantic_similarity(resume_summary, job_targets)
        
        # Merge with TF-IDF overlap
        tfidf_res = compute_tfidf_overlap(raw_text if raw_text else resume_summary, job_desc)
        tfidf_score = tfidf_res.get("similarity_score", 0.0)
        
        semantic_score = round((embedding_score * 0.6) + (tfidf_score * 0.4), 1)
        
        # 3. CONTEXTUAL RELEVANCE SCORE (Matches synonym skills / contextual technology frameworks)
        # E.g. Check for technology maps (REST API development, Cloud, etc.)
        context_count = 0
        context_total = len(req_skills)
        
        for skill in req_skills:
            if check_contextual_match(user_skills, skill):
                context_count += 1
                
        contextual_score = float(context_count / max(1, context_total) * 100.0)
        # Boost if semantic embedding shows high alignment
        if semantic_score > 75:
            contextual_score = min(100.0, contextual_score + 10.0)
        contextual_score = round(contextual_score, 1)
        
        # 4. RECRUITER RELEVANCE SCORE (Analyzes experience years alignment and role hierarchy matches)
        # Parse experience years
        from jobs.scoring_engine import ScoringEngine
        exp_years = ScoringEngine.parse_experience_years(resume_data.get("experience", []))
        req_years = job_details.get("experience_years_required", 2)
        req_level = job_details.get("experience_level", "Intermediate").lower()
        
        experience_ratio = 100.0
        if req_years > 0:
            experience_ratio = min(100.0, (exp_years / req_years) * 100.0)
            
        # Check role mapping (does candidate title match job title?)
        title_match = False
        candidate_titles = [e.get("job_title", "").lower() for e in resume_data.get("experience", [])]
        if any(job_title.lower() in t or t in job_title.lower() for t in candidate_titles if t):
            title_match = True
            
        recruiter_score = (experience_ratio * 0.5) + (100.0 if title_match else 50.0) * 0.5
        recruiter_score = round(min(100.0, recruiter_score), 1)
        
        # OVERALL AGGREGATED SCORE
        overall_score = (
            (keyword_score * 0.25) +
            (semantic_score * 0.35) +
            (contextual_score * 0.20) +
            (recruiter_score * 0.20)
        )
        overall_score = round(min(100.0, max(0.0, overall_score)), 1)
        
        # Readiness
        if overall_score >= 85:
            readiness = "Excellent Fit"
        elif overall_score >= 70:
            readiness = "Strong Alignment"
        elif overall_score >= 50:
            readiness = "Potential Fit"
        else:
            readiness = "Needs Upskilling"
            
        return {
            "job_title": job_title,
            "overall_score": int(overall_score),
            "readiness_level": readiness,
            "semantic_similarity_score": int(semantic_score),
            "keyword_score": int(keyword_score),
            "contextual_relevance_score": int(contextual_score),
            "recruiter_relevance_score": int(recruiter_score),
            "matching_skills": matched_skills,
            "missing_skills": [s for s in req_skills if s not in matched_skills],
            "candidate_exp_years": exp_years,
            "required_exp_years": req_years
        }
