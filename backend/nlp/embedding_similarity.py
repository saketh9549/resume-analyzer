import logging
import numpy as np
from typing import List
from embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

# Try importing SentenceTransformers
SENTENCE_MODEL = None
try:
    from sentence_transformers import SentenceTransformer
    # Initialize the small, high-speed embedding model
    SENTENCE_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    logger.info("SentenceTransformers not available. Using Gemini API EmbeddingService fallback.")

def compute_cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Computes standard cosine similarity between two dimensional vectors.
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    return float(np.dot(v1, v2) / (norm1 * norm2))

async def get_text_embedding(text: str) -> List[float]:
    """
    Retrieves high-quality embeddings. Uses local SentenceTransformers model if loaded,
    otherwise routes to Gemini EmbeddingService (which handles mock caches if offline).
    """
    if not text or not text.strip():
        return [0.0] * 384 if SENTENCE_MODEL else [0.0] * 768
        
    if SENTENCE_MODEL:
        try:
            vector = SENTENCE_MODEL.encode(text, convert_to_numpy=True)
            return vector.tolist()
        except Exception as e:
            logger.error(f"Local SentenceTransformer encoding failed: {e}. Routing to Gemini.")
            
    # Fallback to Gemini EmbeddingService
    return await EmbeddingService.get_embedding(text)

async def calculate_semantic_similarity(text1: str, text2: str) -> float:
    """
    Directly extracts and compares similarity between two texts.
    Returns:
        float: score between 0.0 and 100.0
    """
    v1 = await get_text_embedding(text1)
    v2 = await get_text_embedding(text2)
    
    similarity = compute_cosine_similarity(v1, v2)
    # Cosine ranges from -1 to 1; normalize bounds to 0-100%
    score = max(0.0, min(100.0, (similarity + 1.0) / 2.0 * 100.0))
    return round(score, 1)
