import os
import hashlib
import logging
import asyncio
from typing import List
from functools import partial
import google.generativeai as genai
from database.mongodb import db

logger = logging.getLogger(__name__)

# Fallback collection
embedding_cache_collection = db["embeddings_cache"] if db is not None else None

# Check API configuration
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class EmbeddingService:
    DIMENSION = 768

    @classmethod
    def _get_hash(cls, text: str) -> str:
        """
        Generates SHA-256 hash of text for cache key lookup.
        """
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @classmethod
    def _generate_mock_vector(cls, text: str) -> List[float]:
        """
        Generates a deterministic pseudo-embedding vector of 768 dimensions 
        based on word md5 hashes, enabling basic keyword-based semantic matching offline.
        """
        vector = [0.0] * cls.DIMENSION
        import re
        words = re.sub(r'[^\w\s]', ' ', text.lower()).split()
        
        for word in words:
            if not word.strip():
                continue
            # Hash word into 5 different slots to avoid collisions
            for i in range(5):
                slot_seed = f"{word}_{i}".encode('utf-8')
                idx = int(hashlib.md5(slot_seed).hexdigest(), 16) % cls.DIMENSION
                vector[idx] += 1.0
            
        # Normalize the mock vector
        norm = sum(x*x for x in vector) ** 0.5
        if norm > 0:
            vector = [x / norm for x in vector]
            
        return vector

    @classmethod
    async def get_embedding(cls, text: str) -> List[float]:
        """
        Retrieves the 768-dimension vector embedding for the given text.
        Checks cache first, then calls Gemini API, falling back to mock vectors.
        """
        if not text or not text.strip():
            return [0.0] * cls.DIMENSION

        clean_text = text.strip()
        text_hash = cls._get_hash(clean_text)

        # 1. Check cache first
        if embedding_cache_collection is not None:
            try:
                cached = embedding_cache_collection.find_one({"hash": text_hash})
                if cached and "embedding" in cached:
                    return cached["embedding"]
            except Exception as e:
                logger.error(f"Error checking embedding cache: {e}")

        # 2. Generate embedding (Gemini API or mock)
        embedding = None
        if api_key:
            try:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    partial(
                        genai.embed_content,
                        model="models/text-embedding-004",
                        content=clean_text,
                        task_type="retrieval_document"
                    )
                )
                if response and "embedding" in response:
                    embedding = response["embedding"]
            except Exception as e:
                logger.error(f"Gemini embedding API call failed: {e}. Falling back to mock.")

        # 3. Use mock vector if API failed or offline
        if embedding is None:
            embedding = cls._generate_mock_vector(clean_text)

        # 4. Cache output in DB
        if embedding_cache_collection is not None:
            try:
                embedding_cache_collection.update_one(
                    {"hash": text_hash},
                    {"$set": {
                        "hash": text_hash,
                        "text": clean_text[:200],  # store preview
                        "embedding": embedding
                    }},
                    upsert=True
                )
            except Exception as e:
                logger.error(f"Failed to cache generated embedding: {e}")

        return embedding
