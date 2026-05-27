import logging
import os

logger = logging.getLogger(__name__)

CHROMA_ENABLED = False
chroma_client = None

try:
    import chromadb
    # Set up database persist directory inside the user's workspace
    chroma_db_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db_data"))
    os.makedirs(chroma_db_dir, exist_ok=True)
    
    chroma_client = chromadb.PersistentClient(path=chroma_db_dir)
    CHROMA_ENABLED = True
    logger.info("ChromaDB persistent client initialized successfully.")
except Exception as e:
    logger.warning(f"ChromaDB local vector engine is unavailable: {e}. Falling back to MongoDB similarity caching.")
    CHROMA_ENABLED = False

def is_chroma_active() -> bool:
    """
    Checks if ChromaDB vector client is imported and running.
    """
    return CHROMA_ENABLED and chroma_client is not None

def get_chroma_client():
    """
    Returns the active ChromaDB client, or None if inactive.
    """
    return chroma_client if CHROMA_ENABLED else None
