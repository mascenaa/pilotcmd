"""
Tests for OS detection utilities.
"""

import pytest
from unittest.mock import patch

from pilotcmd.os_utils.detector import OSDetector, OSInfo, OSType


class TestOSDetector:
    """Tests for OSDetector class."""

    def test_detector_initialization(self):
        detector = OSDetector()
        assert detector._os_info is None

    @patch('platform.system')
    def test_windows_detection(self, mock_system):
        mock_system.return_value = "Windows"

        with patch.object(OSDetector, '_detect_windows_shell', return_value='powershell'), \
             patch.object(OSDetector, '_detect_windows_package_manager', return_value='winget'):

            detector = OSDetector()
            os_info = detector.detect()

            assert os_info.type == OSType.WINDOWS
            assert os_info.shell == 'powershell'
            assert os_info.package_manager == 'winget'
            assert os_info.firewall_tool == 'netsh'

    @patch('platform.system')
    def test_linux_detection(self, mock_system):
        mock_system.return_value = "Linux"

        with patch.object(OSDetector, '_detect_unix_shell', return_value='bash'), \
             patch.object(OSDetector, '_detect_linux_package_manager', return_value='apt'), \
             patch.object(OSDetector, '_detect_linux_firewall_tool', return_value='ufw'):

            detector = OSDetector()
            os_info = detector.detect()

            assert os_info.type == OSType.LINUX
            assert os_info.shell == 'bash'
            assert os_info.package_manager == 'apt'
            assert os_info.firewall_tool == 'ufw'

    @patch('platform.system')
    def test_macos_detection(self, mock_system):
        mock_system.return_value = "Darwin"

        with patch.object(OSDetector, '_detect_unix_shell', return_value='zsh'), \
             patch.object(OSDetector, '_detect_macos_package_manager', return_value='brew'):

            detector = OSDetector()
            os_info = detector.detect()

            assert os_info.type == OSType.MACOS
            assert os_info.shell == 'zsh'
            assert os_info.package_manager == 'brew'
            assert os_info.firewall_tool == 'pfctl'

    def test_os_info_methods(self):
        windows_info = OSInfo(
            type=OSType.WINDOWS,
            name="Windows",
            version="10",
            architecture="x64",
            shell="powershell",
        )
        assert windows_info.is_windows() is True
        assert windows_info.is_linux() is False
        assert windows_info.is_macos() is False

        linux_info = OSInfo(
            type=OSType.LINUX,
            name="Linux",
            version="5.4.0",
            architecture="x86_64",
            shell="bash",
        )
        assert linux_info.is_windows() is False
        assert linux_info.is_linux() is True
        assert linux_info.is_macos() is False

    def test_command_mappings(self):
        detector = OSDetector()

        detector._os_info = OSInfo(
            type=OSType.WINDOWS,
            name="Windows",
            version="10",
            architecture="x64",
            shell="cmd",
            package_manager="choco",
            firewall_tool="netsh",
        )

        mappings = detector.get_command_mapping()
        assert "network" in mappings
        assert "ping" in mappings["network"]
        assert mappings["files"]["list"] == "dir"
        assert mappings["packages"]["install"] == "choco install"
        assert mappings["firewall"]["status"] == "netsh advfirewall show allprofiles"

        detector._os_info = OSInfo(
            type=OSType.LINUX,
            name="Linux",
            version="5.4.0",
            architecture="x86_64",
            shell="bash",
            package_manager="apt",
            firewall_tool="ufw",
        )

        mappings = detector.get_command_mapping()
        assert mappings["files"]["list"] == "ls"
        assert mappings["network"]["list_interfaces"] == "ip addr show"
        assert mappings["packages"]["install"] == "sudo apt install"
        assert mappings["firewall"]["status"] == "sudo ufw status"


if __name__ == "__main__":
    pytest.main([__file__])

