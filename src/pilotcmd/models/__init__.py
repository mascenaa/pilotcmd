"""
AI models module for managing different LLM backends.
"""

from .base import BaseModel, ModelResponse

try:
    from .factory import ModelFactory  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ModelFactory = None  # type: ignore

try:
    from .ollama_model import OllamaModel  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    OllamaModel = None  # type: ignore

try:
    from .openai_model import OpenAIModel  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    OpenAIModel = None  # type: ignore

__all__ = ["BaseModel", "ModelResponse"]
if ModelFactory is not None:
    __all__.append("ModelFactory")
if OllamaModel is not None:
    __all__.append("OllamaModel")
if OpenAIModel is not None:
    __all__.append("OpenAIModel")
