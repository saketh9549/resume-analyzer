import logging
import hashlib
from typing import List, Dict, Any
from vector_db.chroma_client import is_chroma_active, get_chroma_client
from embeddings.embedding_service import EmbeddingService
from rag.retrieval_engine import RetrievalEngine

logger = logging.getLogger(__name__)

async def add_knowledge_chunk(text: str, category: str = "General") -> bool:
    """
    Saves a raw text chunk to the vector store (ChromaDB or standard Mongo RAG).
    """
    if not text or not text.strip():
        return False
        
    vector = await EmbeddingService.get_embedding(text)
    
    success = False
    if is_chroma_active():
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("knowledge_chunks")
            # Generate deterministic ID based on text hash
            chunk_id = hashlib.sha256(text.encode("utf-8")).hexdigest()
            
            collection.upsert(
                ids=[chunk_id],
                embeddings=[vector],
                metadatas=[{"category": category}],
                documents=[text]
            )
            success = True
            logger.info(f"Successfully saved RAG chunk in ChromaDB collection 'knowledge_chunks'.")
        except Exception as e:
            logger.error(f"ChromaDB RAG chunk save failed: {e}")
            
    # Always keep standard Mongo RAG backup synced
    from rag.vector_store import VectorStore
    VectorStore.save_chunk(text, vector, {"category": category})
    
    return success

async def query_rag_pipeline(query: str, limit: int = 3) -> str:
    """
    Returns relevant background context for prompt building.
    Uses ChromaDB if active, otherwise falls back to MongoDB RAG retrieval.
    """
    if not query or not query.strip():
        return ""

    if is_chroma_active():
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("knowledge_chunks")
            query_vector = await EmbeddingService.get_embedding(query)
            
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=limit
            )
            
            if results and results["documents"] and len(results["documents"][0]) > 0:
                context_blocks = []
                for idx, text in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][idx]
                    source = metadata.get("category", "General Guidance")
                    context_blocks.append(f"[Reference {idx+1} - Source: {source}]\n{text}")
                logger.info(f"Retrieved {len(context_blocks)} RAG chunks from ChromaDB.")
                return "\n\n".join(context_blocks)
        except Exception as e:
            logger.error(f"ChromaDB RAG search failed: {e}. Falling back to Mongo RAG.")

    # Fallback to Mongo RAG retrieval
    return await RetrievalEngine.retrieve_formatted_context(query, limit=limit)
