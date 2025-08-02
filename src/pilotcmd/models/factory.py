"""
Model factory for creating AI model instances.
"""

from typing import Dict, Type, Optional
from .base import BaseModel, ModelType
from .openai_model import OpenAIModel
from .ollama_model import OllamaModel


class ModelFactory:
    """Factory class for creating AI model instances."""
    
    def __init__(self):
        self._model_registry: Dict[str, Type[BaseModel]] = {
            "openai": OpenAIModel,
            "ollama": OllamaModel,
        }
        
        # Default model configurations
        self._default_configs = {
            "openai": {
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.1,
                "max_tokens": 1000,
            },
            "ollama": {
                "model_name": "llama2",
                "host": "http://localhost:11434",
                "temperature": 0.1,
            }
        }
    
    def get_model(self, model_type: str, **kwargs) -> BaseModel:
        """
        Create and return a model instance.
        
        Args:
            model_type: Type of model ("openai", "ollama")
            **kwargs: Additional configuration parameters
            
        Returns:
            BaseModel: Configured model instance
            
        Raises:
            ValueError: If model type is not supported
        """
        model_type = model_type.lower()
        
        if model_type not in self._model_registry:
            available = ", ".join(self._model_registry.keys())
            raise ValueError(f"Unsupported model type: {model_type}. Available: {available}")
        
        # Get default config and merge with provided kwargs
        default_config = self._default_configs.get(model_type, {})
        config = {**default_config, **kwargs}
        
        # Create model instance
        model_class = self._model_registry[model_type]
        return model_class(**config)
    
    def register_model(self, model_type: str, model_class: Type[BaseModel], default_config: Optional[Dict] = None):
        """
        Register a new model type.
        
        Args:
            model_type: String identifier for the model type
            model_class: Model class that inherits from BaseModel
            default_config: Default configuration for the model
        """
        self._model_registry[model_type] = model_class
        if default_config:
            self._default_configs[model_type] = default_config
    
    def get_available_model_types(self) -> list[str]:
        """Get list of available model types."""
        return list(self._model_registry.keys())
    
    def is_model_available(self, model_type: str) -> bool:
        """Check if a model type is available and working."""
        try:
            model = self.get_model(model_type)
            return model.is_available()
        except Exception:
            return False
    
    def get_recommended_model(self) -> str:
        """Get the recommended model type based on availability."""
        # Check in order of preference
        preferred_order = ["openai", "ollama"]
        
        for model_type in preferred_order:
            if self.is_model_available(model_type):
                return model_type
        
        # If none are available, return the first registered model
        available_types = self.get_available_model_types()
        return available_types[0] if available_types else "openai"
