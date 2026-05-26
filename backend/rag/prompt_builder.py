from rag.retrieval_engine import RetrievalEngine

class PromptBuilder:
    @staticmethod
    async def build_rag_prompt(
        original_prompt: str,
        query: str,
        system_instruction: str = "You are an AI assistant.",
        limit: int = 3
    ) -> tuple:
        """
        Enriches a prompt by appending semantically relevant reference blocks retrieved from the RAG knowledge base.
        Returns a tuple: (enriched_user_prompt, enriched_system_instruction)
        """
        # 1. Retrieve RAG reference text blocks matching query
        context = await RetrievalEngine.retrieve_formatted_context(query, limit=limit)
        
        # 2. Compile user prompt with context if present
        if context:
            enriched_prompt = f"""
            Use the following context guidelines retrieved from our Career Intelligence Database to guide your response. 
            Do not copy the context directly, but ensure your suggestions, scoring updates, or rewrites align with the guidelines.
            
            [CAREER DATABASE CONTEXT]
            {context}
            
            [CANDIDATE TASK]
            {original_prompt}
            """
        else:
            enriched_prompt = original_prompt

        # 3. Enrich system instruction to handle RAG context
        enriched_system = f"{system_instruction}\nYour recommendations are augmented by our Career Intelligence Database."
        
        return enriched_prompt, enriched_system
