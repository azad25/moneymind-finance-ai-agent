"""
HuggingFace Inference API Client
Cloud LLM integration via HuggingFace
"""
from typing import Optional, AsyncIterator, List, Dict, Any
import httpx

from src.config.settings import settings


class HuggingFaceClient:
    """Client for HuggingFace Inference API."""
    
    def __init__(self, api_token: str = None, model: str = None):
        self.api_token = api_token or settings.huggingface_api_token
        self.model = model or settings.huggingface_model
        self.base_url = "https://api-inference.huggingface.co/models"
        self._client = httpx.AsyncClient(timeout=120.0)
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
    
    async def is_available(self) -> bool:
        """Check if API is available."""
        if not self.api_token:
            return False
        try:
            response = await self._client.get(
                f"{self.base_url}/{self.model}",
                headers=self.headers,
            )
            return response.status_code in [200, 503]  # 503 = model loading
        except Exception:
            return False
    
    async def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.95,
    ) -> str:
        """Generate completion."""
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "return_full_text": False,
            }
        }
        
        response = await self._client.post(
            f"{self.base_url}/{self.model}",
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        return ""
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Chat completion using instruction format."""
        # Format messages as prompt
        prompt = self._format_messages(messages)
        return await self.generate(
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for instruction-tuned models."""
        formatted = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                formatted.append(f"<s>[INST] {content}")
            elif role == "user":
                if formatted:
                    formatted.append(f"[INST] {content} [/INST]")
                else:
                    formatted.append(f"<s>[INST] {content} [/INST]")
            elif role == "assistant":
                formatted.append(f"{content}</s>")
        
        return "\n".join(formatted)
    
    async def embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts."""
        embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        
        response = await self._client.post(
            f"{self.base_url}/{embedding_model}",
            headers=self.headers,
            json={"inputs": texts},
        )
        response.raise_for_status()
        return response.json()


# Global HuggingFace client instance
huggingface_client = HuggingFaceClient()
