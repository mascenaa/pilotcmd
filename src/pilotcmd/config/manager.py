"""
Configuration manager for PilotCmd settings.
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class Config:
    """Configuration settings for PilotCmd."""
    default_model: str = "openai"
    openai_api_key: Optional[str] = None
    ollama_host: str = "http://localhost:11434"
    default_timeout: int = 30
    auto_confirm: bool = False
    dry_run_by_default: bool = False
    verbose_output: bool = False
    history_limit: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Config':
        """Create config from dictionary."""
        return cls(**data)


class ConfigManager:
    """Manages PilotCmd configuration settings."""
    
    def __init__(self, config_path: Optional[str] = None):
        # Default config location
        if config_path is None:
            home_dir = Path.home()
            app_dir = home_dir / ".pilotcmd"
            app_dir.mkdir(exist_ok=True)
            config_path = str(app_dir / "config.json")
        
        self.config_path = config_path
        self._config: Optional[Config] = None
    
    def get_config(self) -> Config:
        """Get current configuration, loading from file if needed."""
        if self._config is None:
            self._config = self._load_config()
        return self._config
    
    def _load_config(self) -> Config:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                config = Config.from_dict(data)
                
                # Merge with environment variables
                self._apply_env_overrides(config)
                return config
                
            except (json.JSONDecodeError, TypeError, ValueError):
                # If config file is corrupted, create new default
                pass
        
        # Create default config
        config = Config()
        self._apply_env_overrides(config)
        self._save_config(config)
        return config
    
    def _apply_env_overrides(self, config: Config) -> None:
        """Apply environment variable overrides to config."""
        # OpenAI API Key
        if os.getenv("OPENAI_API_KEY"):
            config.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Ollama host
        if os.getenv("OLLAMA_HOST"):
            config.ollama_host = os.getenv("OLLAMA_HOST")
        
        # Default model
        if os.getenv("PILOTCMD_DEFAULT_MODEL"):
            config.default_model = os.getenv("PILOTCMD_DEFAULT_MODEL")
        
        # Timeout
        if os.getenv("PILOTCMD_TIMEOUT"):
            try:
                config.default_timeout = int(os.getenv("PILOTCMD_TIMEOUT"))
            except ValueError:
                pass
        
        # Auto confirm
        if os.getenv("PILOTCMD_AUTO_CONFIRM"):
            config.auto_confirm = os.getenv("PILOTCMD_AUTO_CONFIRM").lower() in ("true", "1", "yes")
        
        # Dry run by default
        if os.getenv("PILOTCMD_DRY_RUN"):
            config.dry_run_by_default = os.getenv("PILOTCMD_DRY_RUN").lower() in ("true", "1", "yes")
        
        # Verbose output
        if os.getenv("PILOTCMD_VERBOSE"):
            config.verbose_output = os.getenv("PILOTCMD_VERBOSE").lower() in ("true", "1", "yes")
    
    def _save_config(self, config: Config) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            self._config = config
        except IOError as e:
            raise Exception(f"Failed to save configuration: {e}")
    
    def set_default_model(self, model: str) -> None:
        """Set the default AI model."""
        config = self.get_config()
        config.default_model = model
        self._save_config(config)
    
    def set_openai_api_key(self, api_key: str) -> None:
        """Set the OpenAI API key."""
        config = self.get_config()
        config.openai_api_key = api_key
        self._save_config(config)
    
    def set_ollama_host(self, host: str) -> None:
        """Set the Ollama host URL."""
        config = self.get_config()
        config.ollama_host = host
        self._save_config(config)
    
    def set_timeout(self, timeout: int) -> None:
        """Set the default command timeout."""
        config = self.get_config()
        config.default_timeout = timeout
        self._save_config(config)
    
    def set_auto_confirm(self, auto_confirm: bool) -> None:
        """Set auto-confirmation for commands."""
        config = self.get_config()
        config.auto_confirm = auto_confirm
        self._save_config(config)
    
    def set_dry_run_default(self, dry_run: bool) -> None:
        """Set dry run as default behavior."""
        config = self.get_config()
        config.dry_run_by_default = dry_run
        self._save_config(config)
    
    def set_verbose_output(self, verbose: bool) -> None:
        """Set verbose output mode."""
        config = self.get_config()
        config.verbose_output = verbose
        self._save_config(config)
    
    def set_history_limit(self, limit: int) -> None:
        """Set the history limit."""
        config = self.get_config()
        config.history_limit = limit
        self._save_config(config)
    
    def update_config(self, **kwargs) -> None:
        """Update multiple configuration values at once."""
        config = self.get_config()
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        self._save_config(config)
    
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        config = Config()
        self._apply_env_overrides(config)
        self._save_config(config)
    
    def get_config_path(self) -> str:
        """Get the configuration file path."""
        return self.config_path
