from openai import AsyncOpenAI
import google.generativeai as genai
import os
from typing import Dict, Any, List
from abc import ABC, abstractmethod
import numpy as np

class BaseInterviewAgent(ABC):
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Fallback for testing if .env not loaded properly
        if not api_key or api_key == "your_deepseek_api_key_here":
            api_key = "sk-a21a886e957640709f1d31cdb3e39783"
        
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        
        # Remove quotes if present
        api_key = api_key.strip('"').strip("'")
        
        # Use OpenAI client with DeepSeek base URL (v1 endpoint)
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.model = "deepseek-chat"
        # Default temperature - will be overridden by each agent
        self.temperature = 1.0
        
        # Gemini for embeddings
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            gemini_key = "AIzaSyAkmKFD1yBtdxztji-BwRYTbvu_yavevEc"
        
        genai.configure(api_key=gemini_key.strip('"').strip("'"))
        self.embedding_model = "models/embedding-001"
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    async def process_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return response"""
        pass
    
    async def generate_response(self, system_prompt: str, user_input: str, temperature: float = None) -> str:
        """Generate response using the LLM with optional temperature override"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # Use provided temperature or fall back to agent's default
        temp = temperature if temperature is not None else self.temperature
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temp
        )
        
        return response.choices[0].message.content
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for given texts using Gemini"""
        embeddings = []
        for text in texts:
            result = genai.embed_content(
                model=self.embedding_model,
                content=text,
                task_type="retrieval_document"
            )
            embeddings.append(result['embedding'])
        return embeddings
    
    def create_embedding(self, text: str) -> List[float]:
        """Create single embedding using Gemini"""
        result = genai.embed_content(
            model=self.embedding_model,
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    
    def similarity_search(self, query: str, documents: List[str]) -> List[tuple]:
        """Find most similar documents to query using Gemini embeddings"""
        query_embedding = self.create_embedding(query)
        doc_embeddings = self.create_embeddings(documents)
        
        similarities = []
        for i, doc_embedding in enumerate(doc_embeddings):
            # Cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            similarities.append((i, similarity, documents[i]))
        
        return sorted(similarities, key=lambda x: x[1], reverse=True)