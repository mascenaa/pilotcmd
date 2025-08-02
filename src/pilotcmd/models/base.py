"""
Base model interface for AI backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum


class ModelType(Enum):
    """Supported AI model types."""
    OPENAI = "openai"
    OLLAMA = "ollama"
    LOCAL = "local"


@dataclass
class ModelResponse:
    """Response from an AI model."""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.usage is None:
            self.usage = {}
        if self.metadata is None:
            self.metadata = {}


class BaseModel(ABC):
    """Abstract base class for AI models."""
    
    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> ModelResponse:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available for use."""
        pass
    
    @property
    @abstractmethod
    def model_type(self) -> ModelType:
        """Get the model type."""
        pass
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for command generation."""
        return """You are a helpful AI assistant that converts natural language prompts into safe system commands.

RULES:
1. Generate ONLY the command(s) needed, no explanations unless asked
2. Use the most appropriate commands for the detected OS
3. Prioritize safety - avoid destructive operations without explicit confirmation
4. For complex tasks, break them into multiple simple commands
5. Use full paths when necessary
6. Avoid commands that could damage the system
7. If the request is unclear or potentially dangerous, ask for clarification

Response format should be JSON with the following structure:
{
  "commands": [
    {
      "command": "the actual command to execute",
      "explanation": "brief explanation of what this command does",
      "safety_level": "safe|caution|dangerous",
      "requires_sudo": true/false
    }
  ],
  "os_specific": true/false,
  "warning": "optional warning message if needed"
}

Examples of DANGEROUS patterns to avoid or warn about:
- rm -rf / or similar recursive deletions
- dd commands that could overwrite disks
- chmod 777 on system directories
- Commands that modify system-critical files
- Network commands that could expose the system

If you detect a potentially dangerous operation, set safety_level to "dangerous" and include a warning."""

    def format_prompt_with_context(self, user_prompt: str, os_info, command_mapping: Dict[str, Any]) -> str:
        """Format the user prompt with OS context and command mappings."""
        system_prompt = self.get_system_prompt()
        
        context = f"""
SYSTEM CONTEXT:
- Operating System: {os_info.name} {os_info.version}
- OS Type: {os_info.type.value}
- Architecture: {os_info.architecture}
- Shell: {os_info.shell}
- Package Manager: {os_info.package_manager or 'None detected'}

AVAILABLE COMMAND MAPPINGS:
{self._format_command_mappings(command_mapping)}

USER REQUEST: {user_prompt}

Generate appropriate commands for this system configuration.
"""
        
        return f"{system_prompt}\n\n{context}"
    
    def _format_command_mappings(self, mappings: Dict[str, Any]) -> str:
        """Format command mappings for the prompt."""
        formatted = []
        for category, commands in mappings.items():
            formatted.append(f"{category.upper()}:")
            for action, command in commands.items():
                formatted.append(f"  {action}: {command}")
        return "\n".join(formatted)
