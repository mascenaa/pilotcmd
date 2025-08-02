"""
Ollama model implementation.
"""

import json
import asyncio
from typing import Optional, Dict, Any
import subprocess
import httpx

from .base import BaseModel, ModelResponse, ModelType


class OllamaModel(BaseModel):
    """Ollama local LLM model implementation."""
    
    def __init__(self, model_name: str = "llama2", host: str = "http://localhost:11434", **kwargs):
        super().__init__(model_name, **kwargs)
        self.host = host.rstrip('/')
        self.api_url = f"{self.host}/api"
        
        # Default parameters
        self.temperature = kwargs.get("temperature", 0.1)
        self.top_p = kwargs.get("top_p", 0.9)
        self.top_k = kwargs.get("top_k", 40)
    
    async def generate_response(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate a response using Ollama API."""
        try:
            # Prepare the request
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",  # Request JSON format
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "top_p": kwargs.get("top_p", self.top_p),
                    "top_k": kwargs.get("top_k", self.top_k),
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/generate",
                    json=payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
                result = response.json()
                return self._parse_response(result)
                
        except httpx.ConnectError:
            raise Exception("Could not connect to Ollama. Make sure Ollama is running and accessible.")
        except httpx.TimeoutException:
            raise Exception("Ollama request timed out. The model might be loading or overloaded.")
        except Exception as e:
            raise Exception(f"Failed to generate response from Ollama: {str(e)}")
    
    def _parse_response(self, response: Dict[str, Any]) -> ModelResponse:
        """Parse Ollama response into ModelResponse."""
        content = response.get("response", "")
        
        # Ollama usage information (when available)
        usage = {}
        if "eval_count" in response:
            usage["completion_tokens"] = response["eval_count"]
        if "prompt_eval_count" in response:
            usage["prompt_tokens"] = response["prompt_eval_count"]
            usage["total_tokens"] = usage.get("completion_tokens", 0) + response["prompt_eval_count"]
        
        metadata = {
            "model": response.get("model", self.model_name),
            "created_at": response.get("created_at"),
            "done": response.get("done", True),
            "total_duration": response.get("total_duration"),
            "load_duration": response.get("load_duration"),
            "prompt_eval_duration": response.get("prompt_eval_duration"),
            "eval_duration": response.get("eval_duration"),
        }
        
        return ModelResponse(
            content=content,
            model=self.model_name,
            usage=usage,
            metadata=metadata
        )
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            # Check if Ollama service is running
            result = subprocess.run(
                ["curl", "-s", f"{self.host}/api/tags"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Fallback: try with httpx
            return asyncio.run(self._check_ollama_async())
    
    async def _check_ollama_async(self) -> bool:
        """Async check for Ollama availability."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.api_url}/tags")
                return response.status_code == 200
        except Exception:
            return False
    
    @property
    def model_type(self) -> ModelType:
        """Get the model type."""
        return ModelType.OLLAMA
    
    async def get_available_models(self) -> list[str]:
        """Get list of available Ollama models."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.api_url}/tags")
                
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
                else:
                    return []
        except Exception:
            return []
    
    async def pull_model(self, model_name: Optional[str] = None) -> bool:
        """Pull/download a model from Ollama."""
        model_to_pull = model_name or self.model_name
        
        try:
            payload = {"name": model_to_pull}
            
            async with httpx.AsyncClient(timeout=300.0) as client:  # Long timeout for model downloads
                response = await client.post(
                    f"{self.api_url}/pull",
                    json=payload
                )
                
                return response.status_code == 200
        except Exception:
            return False
