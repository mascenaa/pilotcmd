"""
OS detection and utilities for cross-platform command adaptation.
"""

from dataclasses import dataclass
from enum import Enum
import platform
import subprocess
from typing import Dict, List, Optional


class OSType(Enum):
    """Supported operating system types."""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


@dataclass
class OSInfo:
    """Operating system information."""
    type: OSType
    name: str
    version: str
    architecture: str
    shell: str
    package_manager: Optional[str] = None
    
    def is_windows(self) -> bool:
        return self.type == OSType.WINDOWS
    
    def is_linux(self) -> bool:
        return self.type == OSType.LINUX
    
    def is_macos(self) -> bool:
        return self.type == OSType.MACOS


class OSDetector:
    """Detects operating system and provides OS-specific utilities."""
    
    def __init__(self):
        self._os_info: Optional[OSInfo] = None
    
    def detect(self) -> OSInfo:
        """Detect current operating system information."""
        if self._os_info is not None:
            return self._os_info
        
        system = platform.system().lower()
        
        if system == "windows":
            os_type = OSType.WINDOWS
            shell = self._detect_windows_shell()
            package_manager = self._detect_windows_package_manager()
        elif system == "linux":
            os_type = OSType.LINUX
            shell = self._detect_unix_shell()
            package_manager = self._detect_linux_package_manager()
        elif system == "darwin":
            os_type = OSType.MACOS
            shell = self._detect_unix_shell()
            package_manager = "brew"
        else:
            os_type = OSType.UNKNOWN
            shell = "sh"
            package_manager = None
        
        self._os_info = OSInfo(
            type=os_type,
            name=platform.system(),
            version=platform.version(),
            architecture=platform.machine(),
            shell=shell,
            package_manager=package_manager
        )
        
        return self._os_info
    
    def _detect_windows_shell(self) -> str:
        """Detect Windows shell."""
        # Check for PowerShell Core, PowerShell, then CMD
        shells = ["pwsh", "powershell", "cmd"]
        for shell in shells:
            try:
                subprocess.run([shell, "-Command", "exit"], 
                             capture_output=True, timeout=1)
                return shell
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        return "cmd"
    
    def _detect_unix_shell(self) -> str:
        """Detect Unix-like shell."""
        import os
        return os.environ.get("SHELL", "/bin/sh").split("/")[-1]
    
    def _detect_windows_package_manager(self) -> Optional[str]:
        """Detect Windows package manager."""
        # Check for common Windows package managers
        managers = ["winget", "choco", "scoop"]
        for manager in managers:
            try:
                subprocess.run([manager, "--version"], 
                             capture_output=True, timeout=2)
                return manager
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        return None
    
    def _detect_linux_package_manager(self) -> Optional[str]:
        """Detect Linux package manager."""
        # Check for common Linux package managers in order of preference
        managers = [
            ("apt", ["which", "apt"]),
            ("yum", ["which", "yum"]),
            ("dnf", ["which", "dnf"]),
            ("pacman", ["which", "pacman"]),
            ("zypper", ["which", "zypper"]),
            ("emerge", ["which", "emerge"]),
        ]
        
        for manager, check_cmd in managers:
            try:
                result = subprocess.run(check_cmd, capture_output=True, timeout=1)
                if result.returncode == 0:
                    return manager
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None
    
    def get_command_mapping(self) -> Dict[str, Dict[str, str]]:
        """Get OS-specific command mappings for common operations."""
        if not self._os_info:
            self.detect()
        
        if self._os_info.is_windows():
            return self._get_windows_commands()
        elif self._os_info.is_linux():
            return self._get_linux_commands()
        elif self._os_info.is_macos():
            return self._get_macos_commands()
        else:
            return self._get_generic_commands()
    
    def _get_windows_commands(self) -> Dict[str, Dict[str, str]]:
        """Windows-specific command mappings."""
        return {
            "network": {
                "list_interfaces": "ipconfig /all",
                "set_ip": "netsh interface ip set address",
                "ping": "ping",
                "traceroute": "tracert",
                "dns_flush": "ipconfig /flushdns",
            },
            "files": {
                "list": "dir",
                "copy": "copy",
                "move": "move",
                "delete": "del",
                "find": "where",
                "permissions": "icacls",
            },
            "processes": {
                "list": "tasklist",
                "kill": "taskkill",
                "start": "start",
            },
            "services": {
                "list": "sc query",
                "start": "sc start",
                "stop": "sc stop",
                "status": "sc queryex",
            }
        }
    
    def _get_linux_commands(self) -> Dict[str, Dict[str, str]]:
        """Linux-specific command mappings."""
        return {
            "network": {
                "list_interfaces": "ip addr show",
                "set_ip": "ip addr add",
                "ping": "ping",
                "traceroute": "traceroute",
                "dns_flush": "systemd-resolve --flush-caches",
            },
            "files": {
                "list": "ls",
                "copy": "cp",
                "move": "mv",
                "delete": "rm",
                "find": "find",
                "permissions": "chmod",
            },
            "processes": {
                "list": "ps aux",
                "kill": "kill",
                "start": "nohup",
            },
            "services": {
                "list": "systemctl list-units",
                "start": "systemctl start",
                "stop": "systemctl stop",
                "status": "systemctl status",
            }
        }
    
    def _get_macos_commands(self) -> Dict[str, Dict[str, str]]:
        """macOS-specific command mappings."""
        return {
            "network": {
                "list_interfaces": "ifconfig",
                "set_ip": "sudo ifconfig",
                "ping": "ping",
                "traceroute": "traceroute",
                "dns_flush": "sudo dscacheutil -flushcache",
            },
            "files": {  
                "list": "ls",
                "copy": "cp",
                "move": "mv",
                "delete": "rm",
                "find": "find",
                "permissions": "chmod",
            },
            "processes": {
                "list": "ps aux",
                "kill": "kill",
                "start": "nohup",
            },
            "services": {
                "list": "launchctl list",
                "start": "launchctl start",
                "stop": "launchctl stop",
                "status": "launchctl list",
            }
        }
    
    def _get_generic_commands(self) -> Dict[str, Dict[str, str]]:
        """Generic/fallback command mappings."""
        return {
            "network": {
                "ping": "ping",
            },
            "files": {
                "list": "ls",
                "copy": "cp",
                "move": "mv",
                "delete": "rm",
                "find": "find",
            },
            "processes": {
                "list": "ps",
                "kill": "kill",
            }
        }
