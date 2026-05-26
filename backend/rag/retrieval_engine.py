import logging
from typing import List, Dict, Any
from embeddings.embedding_service import EmbeddingService
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

class RetrievalEngine:
    @staticmethod
    async def retrieve_context(query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Main RAG entry point: fetches the embedding vector for the query 
        and scans the local vector store for matching document chunks.
        """
        if not query or not query.strip():
            return []

        try:
            # 1. Fetch query vector embedding
            query_vector = await EmbeddingService.get_embedding(query)
            
            # 2. Query similarity index
            matches = VectorStore.similarity_search(query_vector, limit=limit)
            logger.info(f"Retrieved {len(matches)} RAG chunks for query: '{query[:50]}...'")
            return matches
        except Exception as e:
            logger.error(f"Failed to retrieve context via RAG: {e}")
            return []

    @classmethod
    async def retrieve_formatted_context(cls, query: str, limit: int = 3) -> str:
        """
        Retrieves matching chunks and joins their text blocks into a single formatted string
        to be injected cleanly inside prompts.
        """
        matches = await cls.retrieve_context(query, limit=limit)
        if not matches:
            return ""

        context_blocks = []
        for i, match in enumerate(matches):
            text = match["text"]
            source = match["metadata"].get("category", "General Guidance")
            context_blocks.append(f"[Reference {i+1} - Source: {source}]\n{text}")

        return "\n\n".join(context_blocks)
