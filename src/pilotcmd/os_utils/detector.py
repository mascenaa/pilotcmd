"""
OS detection and utilities for cross-platform command adaptation.
"""

from dataclasses import dataclass
from enum import Enum
import platform
import subprocess
import shutil
from typing import Dict, Optional


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
    firewall_tool: Optional[str] = None
    
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
            firewall_tool = "netsh"
        elif system == "linux":
            os_type = OSType.LINUX
            shell = self._detect_unix_shell()
            package_manager = self._detect_linux_package_manager()
            firewall_tool = self._detect_linux_firewall_tool()
        elif system == "darwin":
            os_type = OSType.MACOS
            shell = self._detect_unix_shell()
            package_manager = self._detect_macos_package_manager()
            firewall_tool = "pfctl"
        else:
            os_type = OSType.UNKNOWN
            shell = "sh"
            package_manager = None
            firewall_tool = None

        self._os_info = OSInfo(
            type=os_type,
            name=platform.system(),
            version=platform.version(),
            architecture=platform.machine(),
            shell=shell,
            package_manager=package_manager,
            firewall_tool=firewall_tool,
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
        for manager in ["winget", "choco", "scoop"]:
            if shutil.which(manager):
                return manager
        return None

    def _detect_linux_package_manager(self) -> Optional[str]:
        """Detect Linux package manager."""
        for manager in ["apt", "dnf", "pacman", "yum", "zypper", "emerge"]:
            if shutil.which(manager):
                return manager
        return None

    def _detect_macos_package_manager(self) -> Optional[str]:
        """Detect macOS package manager."""
        for manager in ["brew"]:
            if shutil.which(manager):
                return manager
        return None

    def _detect_linux_firewall_tool(self) -> Optional[str]:
        """Detect Linux firewall tool."""
        for tool in ["ufw", "nft", "iptables"]:
            if shutil.which(tool):
                return tool
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
        pm = self._os_info.package_manager
        if pm == "winget":
            packages = {
                "install": "winget install",
                "update": "winget upgrade",
                "remove": "winget uninstall",
            }
        elif pm == "choco":
            packages = {
                "install": "choco install",
                "update": "choco upgrade",
                "remove": "choco uninstall",
            }
        else:
            packages = {}

        firewall = {
            "enable": "netsh advfirewall set allprofiles state on",
            "disable": "netsh advfirewall set allprofiles state off",
            "status": "netsh advfirewall show allprofiles",
        }

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
            },
            "packages": packages,
            "firewall": firewall,
        }
    
    def _get_linux_commands(self) -> Dict[str, Dict[str, str]]:
        """Linux-specific command mappings."""
        pm = self._os_info.package_manager
        if pm == "apt":
            packages = {
                "install": "sudo apt install",
                "update": "sudo apt update",
                "remove": "sudo apt remove",
            }
        elif pm == "dnf":
            packages = {
                "install": "sudo dnf install",
                "update": "sudo dnf update",
                "remove": "sudo dnf remove",
            }
        elif pm == "pacman":
            packages = {
                "install": "sudo pacman -S",
                "update": "sudo pacman -Syu",
                "remove": "sudo pacman -R",
            }
        else:
            packages = {}

        firewall_tool = self._os_info.firewall_tool
        if firewall_tool == "ufw":
            firewall = {
                "enable": "sudo ufw enable",
                "disable": "sudo ufw disable",
                "status": "sudo ufw status",
            }
        elif firewall_tool == "nft":
            firewall = {
                "enable": "sudo systemctl start nftables",
                "disable": "sudo systemctl stop nftables",
                "status": "sudo nft list ruleset",
            }
        elif firewall_tool == "iptables":
            firewall = {
                "enable": "sudo systemctl start iptables",
                "disable": "sudo systemctl stop iptables",
                "status": "sudo iptables -L",
            }
        else:
            firewall = {}

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
            },
            "packages": packages,
            "firewall": firewall,
        }
    
    def _get_macos_commands(self) -> Dict[str, Dict[str, str]]:
        """macOS-specific command mappings."""
        pm = self._os_info.package_manager
        if pm == "brew":
            packages = {
                "install": "brew install",
                "update": "brew update",
                "remove": "brew uninstall",
            }
        else:
            packages = {}

        firewall = {
            "enable": "sudo pfctl -E",
            "disable": "sudo pfctl -d",
            "status": "sudo pfctl -s all",
        }

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
            },
            "packages": packages,
            "firewall": firewall,
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
            },
            "packages": {},
            "firewall": {},
        }
