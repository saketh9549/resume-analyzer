import sys
import os
import warnings
import atexit

# 1. Suppress FutureWarnings from google.generativeai package
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=FutureWarning, message=".*google.generativeai.*")

# 2. Suppress ResourceWarnings for unclosed MongoClient globally in tests
warnings.filterwarnings("ignore", category=ResourceWarning, message=".*MongoClient.*")

# Add backend directory to sys.path to avoid module import failures
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Cleanup MongoClient connection at exit to prevent socket leaks/ResourceWarnings
def cleanup_mongo_client():
    db_module = sys.modules.get("database.mongodb")
    if db_module and hasattr(db_module, "client"):
        client = getattr(db_module, "client")
        if client:
            try:
                client.close()
            except Exception:
                pass

atexit.register(cleanup_mongo_client)
