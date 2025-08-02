"""
Command executor for safely running system commands.
"""

import subprocess
import shlex
import asyncio
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

from pilotcmd.nlp.parser import Command, SafetyLevel
from pilotcmd.os_utils.detector import OSInfo


class ExecutionStatus(Enum):
    """Command execution status."""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


@dataclass
class ExecutionResult:
    """Result of command execution."""
    command: Command
    status: ExecutionStatus
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    timestamp: float
    error_message: Optional[str] = None
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS and self.return_code == 0


class CommandExecutor:
    """Executes system commands safely with proper validation."""
    
    def __init__(self, os_info: OSInfo, timeout: int = 30):
        self.os_info = os_info
        self.timeout = timeout
        self.dry_run = False
        
        # Shell configuration based on OS
        if os_info.is_windows():
            self.shell = True
            self.shell_cmd = os_info.shell
        else:
            self.shell = True
            self.shell_cmd = f"/bin/{os_info.shell}"
    
    def set_dry_run(self, dry_run: bool) -> None:
        """Enable or disable dry run mode."""
        self.dry_run = dry_run
    
    async def execute_command(self, command: Command) -> ExecutionResult:
        """
        Execute a single command.
        
        Args:
            command: Command object to execute
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        
        try:
            # Validate command safety
            if command.safety_level == SafetyLevel.DANGEROUS:
                return ExecutionResult(
                    command=command,
                    status=ExecutionStatus.SKIPPED,
                    return_code=-1,
                    stdout="",
                    stderr="Command marked as dangerous and was skipped",
                    execution_time=0.0,
                    timestamp=start_time,
                    error_message="Dangerous command blocked"
                )
            
            # Handle dry run
            if self.dry_run:
                return ExecutionResult(
                    command=command,
                    status=ExecutionStatus.SUCCESS,
                    return_code=0,
                    stdout=f"[DRY RUN] Would execute: {command.command}",
                    stderr="",
                    execution_time=0.0,
                    timestamp=start_time
                )
            
            # Prepare command for execution
            prepared_cmd = self._prepare_command(command)
            
            # Execute command
            if self.os_info.is_windows():
                result = await self._execute_windows_command(prepared_cmd)
            else:
                result = await self._execute_unix_command(prepared_cmd)
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                command=command,
                status=ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED,
                return_code=result.returncode,
                stdout=result.stdout.decode('utf-8', errors='replace') if result.stdout else "",
                stderr=result.stderr.decode('utf-8', errors='replace') if result.stderr else "",
                execution_time=execution_time,
                timestamp=start_time
            )
            
        except asyncio.TimeoutError:
            return ExecutionResult(
                command=command,
                status=ExecutionStatus.TIMEOUT,
                return_code=-1,
                stdout="",
                stderr=f"Command timed out after {self.timeout} seconds",
                execution_time=self.timeout,
                timestamp=start_time,
                error_message="Command timeout"
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                command=command,
                status=ExecutionStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                timestamp=start_time,
                error_message=str(e)
            )
    
    async def execute_commands(self, commands: List[Command]) -> List[ExecutionResult]:
        """
        Execute multiple commands in sequence.
        
        Args:
            commands: List of Command objects to execute
            
        Returns:
            List of ExecutionResult objects
        """
        results = []
        
        for command in commands:
            result = await self.execute_command(command)
            result.stdout = result.stdout + "\n\nExplicação: " + self.explain_output(command.command, result.stdout)
            results.append(result)
            
            # Stop on dangerous command or critical failure
            if (result.status == ExecutionStatus.FAILED and 
                command.safety_level == SafetyLevel.DANGEROUS):
                break
        
        return results
    
    def _prepare_command(self, command: Command) -> str:
        """Prepare command string for execution."""
        cmd = command.command.strip()
        
        # Handle sudo requirements on Unix systems
        if command.requires_sudo and not self.os_info.is_windows():
            if not cmd.startswith('sudo'):
                cmd = f"sudo {cmd}"
        
        return cmd
    
    def explain_output(self, command_str: str, output: str) -> str:
        """Retorna uma explicação do output com base em heurísticas para diversos comandos."""
        explanation = ""
        cmd_lower = command_str.lower()
        if "ipconfig" in cmd_lower or "ifconfig" in cmd_lower:
            import re
            dns = re.findall(r"(?i)(?:dns[- ]*server(?:s)?[^:]*:\s*)([\d\.]+)", output)
            if dns:
                explanation += "Os seus servidores DNS são: " + ", ".join(dns) + ". "
        elif "ping" in cmd_lower:
            import re
            times = re.findall(r"time[=<]\s*(\d+ms)", output)
            if times:
                explanation += "Tempos de resposta do ping: " + ", ".join(times) + ". "
        elif "tracert" in cmd_lower:
            import re
            hops = re.findall(r"(\d+\s+ms)", output)
            if hops:
                explanation += "Tempos de resposta dos saltos (tracert): " + ", ".join(hops) + ". "
        elif "dir" in cmd_lower or "ls" in cmd_lower:
            lines = output.splitlines()
            if lines:
                explanation += "Listagem de arquivos/diretórios com " + str(len(lines)) + " linhas retornadas. "
        # Outras heurísticas podem ser adicionadas para outros comandos.
        if not explanation:
            explanation = "Comando executado com sucesso."
        return explanation
    
    async def _execute_windows_command(self, command: str) -> subprocess.CompletedProcess:
        """Execute command on Windows."""
        # Use appropriate shell
        if self.shell_cmd == "pwsh" or self.shell_cmd == "powershell":
            # PowerShell
            full_cmd = [self.shell_cmd, "-Command", command]
        else:
            # CMD
            full_cmd = [self.shell_cmd, "/c", command]
        
        process = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.timeout
            )
            
            return subprocess.CompletedProcess(
                args=full_cmd,
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise
    
    async def _execute_unix_command(self, command: str) -> subprocess.CompletedProcess:
        """Execute command on Unix-like systems."""
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            return subprocess.CompletedProcess(
                args=command,
                returncode=process.returncode,
                stdout=stdout,
                stderr=stderr
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            raise
    
    def validate_command_safety(self, command: Command) -> bool:
        """Validate if command is safe to execute."""
        # Check safety level
        if command.safety_level == SafetyLevel.DANGEROUS:
            return False
        
        # Additional validation rules
        dangerous_patterns = [
            "rm -rf /",
            "del /s /q C:",
            "format ",
            ":(){ :|:& };:",
            "dd if=/dev/zero of=/dev/sda",
            "chmod 777 /",
            "chown -R root:root /",
        ]
        
        cmd_lower = command.command.lower()
        for pattern in dangerous_patterns:
            if pattern.lower() in cmd_lower:
                return False
        
        return True
