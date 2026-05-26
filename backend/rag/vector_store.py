import logging
from typing import List, Dict, Any
from database.mongodb import db
from embeddings.similarity_engine import SimilarityEngine

logger = logging.getLogger(__name__)

rag_knowledge_collection = db["rag_knowledge"] if db is not None else None

class VectorStore:
    @classmethod
    def save_chunk(cls, text: str, embedding: List[float], metadata: Dict[str, Any] = None) -> bool:
        """
        Saves or updates a chunk document in the MongoDB RAG knowledge collection.
        """
        if rag_knowledge_collection is None:
            logger.warning("Database offline. Failed to save chunk.")
            return False

        try:
            rag_knowledge_collection.update_one(
                {"text": text},
                {"$set": {
                    "text": text,
                    "embedding": embedding,
                    "metadata": metadata or {}
                }},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save chunk to database: {e}")
            return False

    @classmethod
    def similarity_search(cls, query_vector: List[float], limit: int = 3) -> List[Dict[str, Any]]:
        """
        Calculates cosine similarities of all stored knowledge chunks against the query vector,
        returning the top K highest scoring matches.
        """
        if rag_knowledge_collection is None:
            logger.warning("Database offline. Similarity search failed.")
            return []

        try:
            cursor = rag_knowledge_collection.find({})
            results = []
            
            for doc in cursor:
                if "embedding" not in doc or not doc["embedding"]:
                    continue
                
                # Compute cosine overlap
                score = SimilarityEngine.calculate_cosine_similarity(query_vector, doc["embedding"])
                
                results.append({
                    "text": doc["text"],
                    "metadata": doc.get("metadata", {}),
                    "score": round(score * 100.0, 1)
                })

            # Rank matches by score descending
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]
        except Exception as e:
            logger.error(f"Failed to scan vector similarity search: {e}")
            return []
