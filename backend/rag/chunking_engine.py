class ChunkingEngine:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
        """
        Splits a text document into smaller overlapping segments (chunks)
        to prevent information loss at chunk boundaries.
        """
        if not text or not text.strip():
            return []

        clean_text = " ".join(text.split()) # normalize spacing
        chunks = []
        start = 0
        text_len = len(clean_text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            chunk = clean_text[start:end]
            chunks.append(chunk.strip())
            
            # Move start pointer forward by chunk_size - overlap
            start += (chunk_size - overlap)
            if start >= text_len or end == text_len:
                break
                
        return chunks
