import logging
from typing import List, Dict, Tuple, Any
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

logger = logging.getLogger(__name__)

def extract_top_terms(text: str, top_n: int = 15) -> List[Tuple[str, float]]:
    """
    Computes TF-IDF term significance on a single document (using character-level & word-level combinations)
    to find the most unique informational terms.
    """
    if not text or not text.strip():
        return []
        
    try:
        # We treat each line or sentence in the text as a document for TF-IDF context
        documents = [line.strip() for line in text.split("\n") if len(line.strip()) > 5]
        if len(documents) < 3:
            # Fallback if too short: split by sentence or wrap in list
            documents = text.split(". ")
            
        vectorizer = TfidfVectorizer(
            stop_words='english',
            token_pattern=r'\b[a-zA-Z\+\#]{2,}\b',
            max_df=0.95,
            min_df=1
        )
        
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        
        # Calculate average TF-IDF score for each term across all sentences
        mean_scores = np.mean(tfidf_matrix.toarray(), axis=0)
        sorted_indices = np.argsort(mean_scores)[::-1]
        
        top_terms = []
        for idx in sorted_indices[:top_n]:
            score = float(mean_scores[idx])
            if score > 0:
                top_terms.append((feature_names[idx], round(score, 4)))
                
        return top_terms
    except Exception as e:
        logger.error(f"TF-IDF term extraction failed: {e}")
        # Standard frequency fallback
        words = [w.lower() for w in text.split() if len(w) > 3]
        freq = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [(k, float(v / max(1, len(words)))) for k, v in sorted_freq[:top_n]]

def compute_tfidf_overlap(resume_text: str, job_text: str) -> Dict[str, Any]:
    """
    Computes similarity between the TF-IDF vectors of a resume and a job description.
    """
    if not resume_text or not job_text:
        return {"similarity": 0.0, "matched_terms": []}
        
    try:
        vectorizer = TfidfVectorizer(stop_words='english', token_pattern=r'\b[a-zA-Z\+\#]{2,}\b')
        tfidf = vectorizer.fit_transform([resume_text, job_text])
        vectors = tfidf.toarray()
        
        # Cosine similarity between the two documents
        dot_product = np.dot(vectors[0], vectors[1])
        norm_r = np.linalg.norm(vectors[0])
        norm_j = np.linalg.norm(vectors[1])
        
        similarity = 0.0
        if norm_r > 0 and norm_j > 0:
            similarity = float(dot_product / (norm_r * norm_j))
            
        # Identify terms present in both
        feature_names = vectorizer.get_feature_names_out()
        r_indices = np.where(vectors[0] > 0)[0]
        j_indices = np.where(vectors[1] > 0)[0]
        common = set(r_indices).intersection(set(j_indices))
        
        matched_terms = []
        for idx in common:
            # Combined significance weight
            weight = float(vectors[0][idx] * vectors[1][idx])
            matched_terms.append({
                "term": feature_names[idx],
                "significance": round(weight, 4)
            })
            
        # Sort matched terms by combined weight
        matched_terms = sorted(matched_terms, key=lambda x: x["significance"], reverse=True)
        
        return {
            "similarity_score": round(similarity * 100.0, 1),
            "matched_terms": matched_terms[:12]
        }
    except Exception as e:
        logger.error(f"TF-IDF overlap computation failed: {e}")
        return {"similarity_score": 0.0, "matched_terms": []}
