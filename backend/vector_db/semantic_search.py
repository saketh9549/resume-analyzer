import logging
from typing import List, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from database.mongodb import db, resumes_collection
from embeddings.embedding_service import EmbeddingService
from embeddings.similarity_engine import SimilarityEngine
from vector_db.chroma_client import is_chroma_active, get_chroma_client

logger = logging.getLogger(__name__)

# Recruiter posted jobs collection
recruiter_jobs_collection = db["recruiter_jobs"] if db is not None else None

async def add_resume_vector(resume_id_str: str, text: str, filename: str, user_email: str) -> bool:
    """
    Embeds a resume and registers it in ChromaDB (or caches it on Mongo if offline).
    """
    if not text or not text.strip():
        return False
        
    vector = await EmbeddingService.get_embedding(text)
    
    success = False
    if is_chroma_active():
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("resumes")
            collection.upsert(
                ids=[resume_id_str],
                embeddings=[vector],
                metadatas=[{"filename": filename, "user_email": user_email}],
                documents=[text[:2000]] # index snippet to save memory
            )
            logger.info(f"Successfully added resume {resume_id_str} to ChromaDB collection.")
            success = True
        except Exception as e:
            logger.error(f"ChromaDB insert failed: {e}. Falling back to standard MongoDB cache.")
            
    # Always keep fallback indicator on MongoDB document
    if resumes_collection is not None:
        resumes_collection.update_one(
            {"_id": ObjectId(resume_id_str)},
            {"$set": {
                "has_vector": True, 
                "embedding_generated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    return success

async def add_job_vector(job_id_str: str, text: str, title: str, department: str = "") -> bool:
    """
    Embeds a recruiter job description and stores it in ChromaDB (or standard Mongo fallback).
    """
    if not text or not text.strip():
        return False
        
    vector = await EmbeddingService.get_embedding(text)
    
    success = False
    if is_chroma_active():
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("jobs")
            collection.upsert(
                ids=[job_id_str],
                embeddings=[vector],
                metadatas=[{"title": title, "department": department}],
                documents=[text[:2000]]
            )
            logger.info(f"Successfully added job {job_id_str} to ChromaDB collection.")
            success = True
        except Exception as e:
            logger.error(f"ChromaDB job insert failed: {e}.")
            
    if recruiter_jobs_collection is not None:
        recruiter_jobs_collection.update_one(
            {"_id": ObjectId(job_id_str)},
            {"$set": {"has_vector": True}}
        )
    return success

async def search_candidates_semantic(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic candidate matching over resumes with advanced multi-dimensional sub-scores.
    """
    if not query or not query.strip():
        return []

    if resumes_collection is None:
        return []

    # Parse query to construct a mock job description
    from nlp.semantic_match_engine import SemanticMatchEngine
    from services.scoring_engine import CORE_RECOMMENDED_SKILLS
    
    query_lower = query.lower()
    detected_skills = []
    
    # Simple keyword spotter from core recommended list + synonyms
    all_techs = CORE_RECOMMENDED_SKILLS + ["FastAPI", "Flask", "Django", "Express", "Microservices", "Kubernetes", "GCP", "PostgreSQL", "MongoDB"]
    for tech in all_techs:
        if tech.lower() in query_lower:
            detected_skills.append(tech)
            
    if not detected_skills:
        detected_skills = [w.capitalize() for w in query.split() if len(w) > 3]

    mock_job = {
        "job_title": query,
        "description": query,
        "required_skills": list(set(detected_skills)),
        "experience_years_required": 2 if "senior" in query_lower else (4 if "lead" in query_lower else 1),
        "experience_level": "Senior" if "senior" in query_lower else ("Junior" if "junior" in query_lower else "Intermediate")
    }

    cursor = resumes_collection.find({})
    candidates = []
    for doc in cursor:
        candidates.append({
            "id": str(doc["_id"]),
            "filename": doc.get("filename", ""),
            "user_email": doc.get("user_email", ""),
            "skills": doc.get("skills", []),
            "ats_score": doc.get("ats_score", 0),
            "parsed_text": doc.get("parsed_text", doc.get("text", "")),
            "experience": doc.get("experience", []),
            "education": doc.get("education", [])
        })

    ranked = []
    for cand in candidates:
        match_res = await SemanticMatchEngine.match_resume_to_job(
            resume_data=cand,
            job_details=mock_job,
            raw_text=cand["parsed_text"]
        )
        
        ranked.append({
            "id": cand["id"],
            "filename": cand["filename"],
            "user_email": cand["user_email"],
            "skills": cand["skills"],
            "experience": cand["experience"],
            "education": cand["education"],
            "ats_score": cand["ats_score"],
            "similarity_score": match_res["overall_score"],
            "semantic_similarity_score": match_res["semantic_similarity_score"],
            "keyword_score": match_res["keyword_score"],
            "contextual_relevance_score": match_res["contextual_relevance_score"],
            "recruiter_relevance_score": match_res["recruiter_relevance_score"],
            "matching_skills": match_res["matching_skills"],
            "missing_skills": match_res["missing_skills"]
        })

    ranked = sorted(ranked, key=lambda x: x["similarity_score"], reverse=True)
    return ranked[:top_k]

async def search_jobs_semantic(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Semantic job matching over recruiter jobs.
    """
    if not query or not query.strip():
        return []

    if is_chroma_active():
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("jobs")
            query_vector = await EmbeddingService.get_embedding(query)
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )
            
            ranked = []
            if results and results["ids"] and len(results["ids"][0]) > 0:
                for idx, j_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][idx]
                    dist = results["distances"][0][idx]
                    score = max(0.0, min(100.0, 100.0 - (dist * 50.0)))
                    
                    if recruiter_jobs_collection is not None:
                        doc = recruiter_jobs_collection.find_one({"_id": ObjectId(j_id)})
                        if doc:
                            ranked.append({
                                "id": j_id,
                                "title": doc.get("title", ""),
                                "description": doc.get("description", ""),
                                "required_skills": doc.get("required_skills", []),
                                "industry": doc.get("industry", ""),
                                "similarity_score": round(score, 1)
                            })
                            continue
                            
                    ranked.append({
                        "id": j_id,
                        "title": metadata.get("title", ""),
                        "similarity_score": round(score, 1)
                    })
                return ranked
        except Exception as e:
            logger.error(f"ChromaDB job search failed: {e}. Falling back to Mongo.")

    if recruiter_jobs_collection is None:
        return []
        
    cursor = recruiter_jobs_collection.find({})
    all_jobs = []
    for j in cursor:
        all_jobs.append({
            "id": str(j["_id"]),
            "title": j.get("title", ""),
            "description": j.get("description", ""),
            "required_skills": j.get("required_skills", []),
            "industry": j.get("industry", "")
        })
        
    return await SimilarityEngine.match_query_to_documents(
        query=query,
        documents=all_jobs,
        text_field="description",
        top_k=top_k
    )
