"""
OpenAI model implementation.
"""

import json
import os
from typing import Optional, Dict, Any
import asyncio
import openai
from openai import OpenAI

from .base import BaseModel, ModelResponse, ModelType


class OpenAIModel(BaseModel):
    """OpenAI GPT model implementation."""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", api_key: Optional[str] = None, **kwargs):
        super().__init__(model_name, **kwargs)
        
        # Get API key from parameter, environment, or config
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Default parameters
        self.temperature = kwargs.get("temperature", 0.1)  # Low temperature for consistent command generation
        self.max_tokens = kwargs.get("max_tokens", 1000)
        self.top_p = kwargs.get("top_p", 0.9)
    
    async def generate_response(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate a response using OpenAI's API."""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._make_openai_request, 
                prompt, 
                kwargs
            )
            
            return self._parse_response(response)
            
        except openai.RateLimitError:
            raise Exception("OpenAI API rate limit exceeded. Please try again later.")
        except openai.AuthenticationError:
            raise Exception("OpenAI API authentication failed. Check your API key.")
        except openai.APIError as e:
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def _make_openai_request(self, prompt: str, kwargs: Dict[str, Any]):
        """Make synchronous request to OpenAI API."""
        messages = [
            {
                "role": "system",
                "content": self.get_system_prompt()
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # Override default parameters with kwargs
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        top_p = kwargs.get("top_p", self.top_p)
        
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            response_format={"type": "json_object"}  # Force JSON response
        )
    
    def _parse_response(self, response) -> ModelResponse:
        """Parse OpenAI response into ModelResponse."""
        content = response.choices[0].message.content
        
        # Extract usage information
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }
        
        metadata = {
            "model": response.model,
            "finish_reason": response.choices[0].finish_reason,
            "created": response.created
        }
        
        return ModelResponse(
            content=content,
            model=self.model_name,
            usage=usage,
            metadata=metadata
        )
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available."""
        try:
            # Make a simple test request
            self.client.models.list()
            return True
        except Exception:
            return False
    
    @property
    def model_type(self) -> ModelType:
        """Get the model type."""
        return ModelType.OPENAI
    
    def get_available_models(self) -> list[str]:
        """Get list of available OpenAI models."""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if "gpt" in model.id.lower()]
        except Exception:
            return ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]  # Fallback list
