import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# Basic list of English stop words to filter out if NLTK stop words are not available
DEFAULT_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "cannot", "could", "did", "do", "does", "doing", "don't", "down", "during", "each", "few",
    "for", "from", "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "isn't", "it", "its", "itself",
    "let's", "me", "more", "most", "must", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
    "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
    "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom", "why", "with",
    "would", "you", "your", "yours", "yourself", "yourselves"
}

# Try loading spaCy or NLTK
SPACY_NLP = None
NLTK_LEMMA = None

try:
    import spacy
    # Load small English model (without download blocking, assume it's pre-downloaded or use try-catch)
    SPACY_NLP = spacy.load("en_core_web_sm")
except Exception:
    logger.info("spaCy not available. Falling back to NLTK / regex lemmatization.")

if not SPACY_NLP:
    try:
        import nltk
        from nltk.stem import WordNetLemmatizer
        # Download resource in thread-safe manner
        nltk.download("wordnet", quiet=True)
        NLTK_LEMMA = WordNetLemmatizer()
    except Exception:
        logger.info("NLTK not available. Using regex stemmer fallback.")

# Common resume verb suffixes mappings for regex-based fallback stemming
COMMON_VERB_ROOTS = {
    r"(\b\w+)(?:ing|ed|s)\b": lambda m: m.group(1),
}

def clean_text(text: str) -> str:
    """
    Strips excessive whitespace, handles encoding issues, and normalizes characters.
    """
    if not text:
        return ""
    # Normalize unicode spaces
    text = re.sub(r'[\u200b-\u200d\ufeff]', '', text)
    # Standardize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize(text: str) -> List[str]:
    """
    Tokenizes text into words.
    """
    if not text:
        return []
    
    if SPACY_NLP:
        doc = SPACY_NLP(text)
        return [token.text for token in doc]
    
    # Fallback tokenizer
    return re.findall(r'\b[a-zA-Z0-9_\-\+\#]+\b', text.lower())

def lemmatize_word(word: str) -> str:
    """
    Reduces a word to its base root form (lemma).
    """
    w = word.lower().strip()
    if not w:
        return ""
    
    if SPACY_NLP:
        doc = SPACY_NLP(w)
        if len(doc) > 0:
            return doc[0].lemma_
            
    if NLTK_LEMMA:
        try:
            # Lemmatize as verb first, then noun
            lemma = NLTK_LEMMA.lemmatize(w, pos='v')
            if lemma == w:
                lemma = NLTK_LEMMA.lemmatize(w, pos='n')
            return lemma
        except Exception:
            pass
            
    # Regex-based stemmer fallback (heuristic)
    # Strip common inflections
    if len(w) > 4:
        if w.endswith("ing"):
            # developing -> develop
            # engineering -> engineer
            stem = w[:-3]
            if stem.endswith("y"):
                return stem
            if stem.endswith("doubl") or stem.endswith("pl"):
                return stem + "e"
            return stem
        elif w.endswith("ed"):
            # engineered -> engineer
            # developed -> develop
            stem = w[:-2]
            if stem.endswith(("t", "l", "r", "n", "s", "p", "y", "w", "k", "m", "d", "h")):
                return stem
            return w[:-1] # strip d
        elif w.endswith("ies"):
            # technologies -> technology
            return w[:-3] + "y"
        elif w.endswith("s") and not w.endswith("ss") and not w.endswith("us") and not w.endswith("is") and not w.endswith("as"):
            return w[:-1]
            
    return w

def preprocess_text(text: str, remove_stopwords: bool = True) -> List[str]:
    """
    Performs full preprocessing: tokenization, lemmatization, stopword filtering.
    """
    tokens = tokenize(text)
    processed = []
    
    for token in tokens:
        lemma = lemmatize_word(token)
        if not lemma:
            continue
        if remove_stopwords and lemma in DEFAULT_STOPWORDS:
            continue
        processed.append(lemma)
        
    return processed
