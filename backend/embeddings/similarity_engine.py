from typing import List, Dict, Any
from embeddings.embedding_service import EmbeddingService

class SimilarityEngine:
    @staticmethod
    def calculate_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """
        Computes the cosine similarity value between two vector arrays of the same length.
        Returns a score normalized between 0.0 and 1.0 (clamped).
        """
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5
        
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
            
        similarity = dot_product / (norm_a * norm_b)
        # Normalize and clamp bounds to [0.0, 1.0]
        return max(0.0, min(1.0, float(similarity)))

    @classmethod
    async def match_query_to_documents(
        cls,
        query: str,
        documents: List[Dict[str, Any]],
        text_field: str = "parsed_text",
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Semantically ranks target documents against a query string.
        
        Args:
            query (str): The search term or job description query.
            documents (List[Dict]): MongoDB record dicts.
            text_field (str): The field inside documents containing text to compare.
            top_k (int): Number of top matches to return.
            
        Returns:
            List[Dict] of ranked documents containing a 'similarity_score'.
        """
        if not query or not documents:
            return []

        # 1. Generate query embedding
        query_vector = await EmbeddingService.get_embedding(query)
        ranked_docs = []

        # 2. Iterate and score documents
        for doc in documents:
            content = doc.get(text_field, "")
            if not content:
                # Fallback check on nested tags (e.g. skills)
                if "skills" in doc:
                    content = " ".join(doc.get("skills", []))
                else:
                    continue

            # Generate or load doc embedding
            doc_vector = await EmbeddingService.get_embedding(content)
            
            # Calculate cosine score
            score = cls.calculate_cosine_similarity(query_vector, doc_vector)
            
            # Append score to document dict
            doc_with_score = {**doc, "similarity_score": round(score * 100.0, 1)}
            ranked_docs.append(doc_with_score)

        # 3. Sort by similarity score descending
        ranked_docs.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return ranked_docs[:top_k]
