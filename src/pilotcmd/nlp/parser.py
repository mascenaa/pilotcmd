"""
Natural Language Parser for converting prompts to system commands.
"""

import asyncio
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from pilotcmd.models.base import BaseModel
from pilotcmd.os_utils.detector import OSInfo
from pilotcmd.utils.token_counter import estimate_tokens


class SafetyLevel(Enum):
    """Command safety levels."""

    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"


@dataclass
class Command:
    """Represents a parsed command step."""

    command: str
    explanation: str
    step: Optional[int] = None
    safety_level: SafetyLevel = SafetyLevel.SAFE
    requires_sudo: bool = False
    category: Optional[str] = None

    def __post_init__(self):
        # Convert string safety level to enum if needed
        if isinstance(self.safety_level, str):
            self.safety_level = SafetyLevel(self.safety_level.lower())
        if isinstance(self.step, str) and self.step.isdigit():
            self.step = int(self.step)


@dataclass
class ParseResult:
    """Result of parsing a natural language prompt."""

    commands: List[Command]
    os_specific: bool = False
    warning: Optional[str] = None
    raw_response: Optional[str] = None


class NLPParser:
    """Natural Language Parser that converts prompts to system commands."""

    def __init__(self, model: BaseModel, os_info: OSInfo):
        self.model = model
        self.os_info = os_info
        self.last_usage: Optional[Dict[str, int]] = None
        self._dangerous_patterns = [
            "rm -rf /",
            "del /s /q",
            "format ",
            ":(){ :|:& };:",  # Fork bomb
            "dd if=/dev/zero",
            "chmod 777 /",
            "chown -R root /",
            "sudo rm -rf",
            "rmdir /s /q",
        ]

    async def parse(self, prompt: str) -> List[Command]:
        """
        Parse a natural language prompt into system commands.

        Args:
            prompt: Natural language description of desired action

        Returns:
            List of Command objects
        """
        try:
            self.last_usage = None
            # Get OS-specific command mappings
            from pilotcmd.os_utils.detector import OSDetector

            detector = OSDetector()
            command_mapping = detector.get_command_mapping()

            # Format prompt with context
            formatted_prompt = self.model.format_prompt_with_context(
                prompt, self.os_info, command_mapping
            )

            # Generate response from AI model
            response = await self.model.generate_response(formatted_prompt)

            # Estimate token usage
            prompt_tokens = estimate_tokens(formatted_prompt)
            completion_tokens = estimate_tokens(response.content)
            self.last_usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            }

            # Parse the response
            parse_result = self._parse_model_response(response.content)

            # Additional safety checks
            for command in parse_result.commands:
                self._apply_safety_checks(command)

            return parse_result.commands

        except Exception as e:
            # Fallback: try to generate simple commands
            from pilotcmd.nlp.simple_parser import SimpleParser

            fallback_parser = SimpleParser(self.os_info)
            self.last_usage = None
            return fallback_parser.parse(prompt)

    def _parse_model_response(self, response_content: str) -> ParseResult:
        """Parse the JSON response from the AI model."""
        try:
            # Clean and parse JSON response
            response_content = response_content.strip()
            if response_content.startswith("```json"):
                response_content = response_content[7:]
            if response_content.endswith("```"):
                response_content = response_content[:-3]

            data = json.loads(response_content)

            # Extract commands
            commands = []
            for cmd_data in data.get("commands", []):
                command = Command(
                    command=cmd_data.get("command", ""),
                    explanation=cmd_data.get("explanation", ""),
                    step=cmd_data.get("step"),
                    safety_level=cmd_data.get("safety_level", "safe"),
                    requires_sudo=cmd_data.get("requires_sudo", False),
                    category=cmd_data.get("category"),
                )
                commands.append(command)

            return ParseResult(
                commands=commands,
                os_specific=data.get("os_specific", False),
                warning=data.get("warning"),
                raw_response=response_content,
            )

        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract commands from text
            return self._parse_text_response(response_content)

    def _parse_text_response(self, response: str) -> ParseResult:
        """Fallback parser for non-JSON responses."""
        commands = []
        lines = response.strip().split("\n")

        current_command = None
        for line in lines:
            line = line.strip()

            # Look for command-like patterns
            if line.startswith("$") or line.startswith(">"):
                # Extract command
                command_text = line[1:].strip()
                if command_text:
                    commands.append(
                        Command(
                            command=command_text,
                            explanation=f"Execute: {command_text}",
                            safety_level=SafetyLevel.CAUTION,
                        )
                    )
            elif line and not line.startswith("#") and not line.startswith("//"):
                # Treat as potential command
                if any(
                    word in line.lower()
                    for word in ["ls", "dir", "cd", "cp", "mv", "mkdir", "touch"]
                ):
                    commands.append(
                        Command(
                            command=line,
                            explanation=f"Execute: {line}",
                            safety_level=SafetyLevel.CAUTION,
                        )
                    )

        return ParseResult(commands=commands)

    def _apply_safety_checks(self, command: Command) -> None:
        """Apply safety checks to a command."""
        cmd_lower = command.command.lower()

        # Check for dangerous patterns
        for pattern in self._dangerous_patterns:
            if pattern.lower() in cmd_lower:
                command.safety_level = SafetyLevel.DANGEROUS
                break

        # Check for sudo/admin requirements
        sudo_indicators = ["sudo", "su -", "runas", "admin:", "administrator"]
        if any(indicator in cmd_lower for indicator in sudo_indicators):
            command.requires_sudo = True
            if command.safety_level == SafetyLevel.SAFE:
                command.safety_level = SafetyLevel.CAUTION

        # Check for system modification commands
        system_modifiers = [
            "chmod 777",
            "chown -r",
            "rm -rf",
            "del /s",
            "format",
            "fdisk",
            "mkfs",
            "mount",
            "umount",
            "systemctl",
            "service",
        ]
        if any(modifier in cmd_lower for modifier in system_modifiers):
            if command.safety_level == SafetyLevel.SAFE:
                command.safety_level = SafetyLevel.CAUTION

    def _fallback_parsing(self, prompt: str) -> List[Command]:
        """Fallback parsing when AI model fails."""
        commands = []
        prompt_lower = prompt.lower()

        # Simple pattern matching for common requests
        if "list" in prompt_lower and (
            "file" in prompt_lower or "directory" in prompt_lower
        ):
            if self.os_info.is_windows():
                commands.append(Command("dir", "List directory contents"))
            else:
                commands.append(Command("ls -la", "List directory contents"))

        elif "ping" in prompt_lower:
            # Extract IP/hostname if possible
            words = prompt.split()
            target = "google.com"  # Default
            for word in words:
                if "." in word and not word.startswith("."):
                    target = word
                    break
            commands.append(Command(f"ping {target}", f"Ping {target}"))

        elif "current directory" in prompt_lower or "where am i" in prompt_lower:
            if self.os_info.is_windows():
                commands.append(Command("cd", "Show current directory"))
            else:
                commands.append(Command("pwd", "Show current directory"))

        # If no patterns match, return empty list
        return commands

    def validate_command(self, command: Command) -> bool:
        """Validate if a command is safe to execute."""
        if command.safety_level == SafetyLevel.DANGEROUS:
            return False

        # Additional validation logic can be added here
        return True
