import logging
from typing import List
from database.mongodb import db
from rag.chunking_engine import ChunkingEngine
from rag.vector_store import VectorStore
from embeddings.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

rag_knowledge_collection = db["rag_knowledge"] if db is not None else None

# Pre-packaged career intelligence guidelines
DEFAULT_KNOWLEDGE_DOCUMENTS = [
    {
        "text": "ATS Optimization Guidelines: Many Applicant Tracking Systems (ATS) cannot parse text inside graphical shapes, custom headers, footers, or embedded text boxes. Always use standard single-column layouts or simple tables without hidden structures. Keep margins above 0.5 inches. Stick to web-safe fonts such as Arial, Calibri, Helvetica, or Times New Roman to ensure parser translation runs correctly.",
        "category": "ats_optimization"
    },
    {
        "text": "ATS Formatting Constraints: Do not use mixed-date schemas. Dates should always list years or months uniformly (e.g. '05/2021 - Present' or 'May 2021 - Present'). Never write visual graphs or rating stars to indicate skill percentages (e.g. 'Python: 4/5 stars') since parser engines see these as unreadable graphical shapes, leading to zero parsed tech indicators.",
        "category": "ats_optimization"
    },
    {
        "text": "Technical Interview STAR Framework: When answering technical or behavioral interview questions, structure replies using the STAR framework. Situation: set the scene. Task: clarify your explicit role. Action: explain what steps you executed, technologies applied (e.g. FastAPI, MongoDB), and architectural trade-offs. Result: describe the quantitative outcome (e.g. reduced DB response latency by 20%).",
        "category": "interview_prep"
    },
    {
        "text": "System Design Interview Strategy: In system design sessions, always lead by clarifying requirements. Estimate scale constraints (QPS, storage metrics, write/read splits). Outline high-level microservices, database choice rationales (e.g. MongoDB for unstructured log documents versus SQL for transactional ledgers), and caching strategies (using Redis). Highlight failure boundary handling (circuit breakers, message queues).",
        "category": "interview_prep"
    },
    {
        "text": "What Recruiters Seek in Software Engineers: Modern technical recruiters focus on quantifiable deliverables rather than listed duties. Instead of 'Responsible for backend features', use action-verbs: 'Refactored backend REST API routers, reducing request latency by 15%'. Recruiters scan for containerization (Docker), deployment automation (CI/CD pipelines), test coverage (JUnit/pytest), and cloud administration.",
        "category": "recruiter_insights"
    },
    {
        "text": "DevOps & Cloud-Native Skill Progression: Advancing from mid-level to senior roles requires containerization and orchestration mastery. Key technologies to study include Docker (replicating local environments), Kubernetes (managing service replicas, volumes, ingress configs), and Infrastructure as Code (Terraform). Understanding Prometheus/Grafana monitoring tools and AWS cloud architectures adds high resume value.",
        "category": "skill_progression"
    }
]

class KnowledgeLoader:
    @classmethod
    async def seed_default_knowledge(cls, force: bool = False):
        """
        Populates MongoDB RAG vector collections with pre-packaged career guidelines 
        if the collection is currently empty or force=True.
        """
        if rag_knowledge_collection is None:
            logger.warning("Database offline. Skipping RAG knowledge seeding.")
            return

        try:
            # Check if database is already seeded
            count = rag_knowledge_collection.count_documents({})
            if count > 0 and not force:
                logger.info(f"RAG knowledge collection already seeded with {count} chunks. Skipping.")
                return

            logger.info("Initializing RAG career knowledge base seeding...")
            seeded_count = 0
            
            for doc in DEFAULT_KNOWLEDGE_DOCUMENTS:
                text_content = doc["text"]
                category = doc["category"]
                
                # Split content semantically using ChunkingEngine
                chunks = ChunkingEngine.chunk_text(text_content, chunk_size=300, overlap=50)
                
                for chunk in chunks:
                    # Generate vector embedding for each chunk
                    embedding = await EmbeddingService.get_embedding(chunk)
                    
                    # Store chunk
                    success = VectorStore.save_chunk(
                        text=chunk,
                        embedding=embedding,
                        metadata={"category": category}
                    )
                    if success:
                        seeded_count += 1
            
            logger.info(f"RAG career knowledge base seeded successfully with {seeded_count} chunks.")
        except Exception as e:
            logger.error(f"Failed to seed RAG knowledge: {e}")
