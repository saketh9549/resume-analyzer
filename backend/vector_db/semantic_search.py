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
    Semantic candidate matching over resumes.
    """
    if not query or not query.strip():
        return []

    # If ChromaDB is active, query ChromaDB resumes collection
    if is_chroma_active():
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("resumes")
            query_vector = await EmbeddingService.get_embedding(query)
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k
            )
            
            ranked = []
            if results and results["ids"] and len(results["ids"][0]) > 0:
                for idx, r_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][idx]
                    # Score normalized 0-100 from distance
                    # Chroma default is L2 squared distance, so lower is closer.
                    dist = results["distances"][0][idx]
                    # Convert distance to a similarity score percentage
                    score = max(0.0, min(100.0, 100.0 - (dist * 50.0)))
                    
                    # Fetch extra MongoDB fields for display
                    if resumes_collection is not None:
                        doc = resumes_collection.find_one({"_id": ObjectId(r_id)})
                        if doc:
                            ranked.append({
                                "id": r_id,
                                "filename": doc.get("filename", ""),
                                "user_email": doc.get("user_email", ""),
                                "skills": doc.get("skills", []),
                                "ats_score": doc.get("ats_score", 0),
                                "experience": doc.get("experience", []),
                                "education": doc.get("education", []),
                                "similarity_score": round(score, 1)
                            })
                            continue
                            
                    ranked.append({
                        "id": r_id,
                        "filename": metadata.get("filename", ""),
                        "user_email": metadata.get("user_email", ""),
                        "similarity_score": round(score, 1)
                    })
                return ranked
        except Exception as e:
            logger.error(f"ChromaDB candidate search failed: {e}. Falling back to Mongo search.")

    # MongoDB fallback: retrieve candidates and score them in-memory
    if resumes_collection is None:
        return []
        
    cursor = resumes_collection.find({})
    all_resumes = []
    for r in cursor:
        all_resumes.append({
            "id": str(r["_id"]),
            "filename": r.get("filename", ""),
            "user_email": r.get("user_email", ""),
            "skills": r.get("skills", []),
            "ats_score": r.get("ats_score", 0),
            "parsed_text": r.get("parsed_text", r.get("text", "")),
            "experience": r.get("experience", []),
            "education": r.get("education", [])
        })
        
    return await SimilarityEngine.match_query_to_documents(
        query=query,
        documents=all_resumes,
        text_field="parsed_text",
        top_k=top_k
    )

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
