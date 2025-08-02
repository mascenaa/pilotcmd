"""
Test configuration for pytest.
"""

import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config_dir(temp_dir):
    """Create a mock configuration directory."""
    config_dir = temp_dir / ".pilotcmd"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_db_path(mock_config_dir):
    """Create a mock database path."""
    return str(mock_config_dir / "test_context.db")


@pytest.fixture
def mock_config_path(mock_config_dir):
    """Create a mock config file path."""
    return str(mock_config_dir / "test_config.json")


@pytest.fixture
def sample_commands():
    """Sample commands for testing."""
    from pilotcmd.nlp.parser import Command, SafetyLevel
    
    return [
        Command(
            command="ls -la",
            explanation="List directory contents",
            safety_level=SafetyLevel.SAFE
        ),
        Command(
            command="ping google.com",
            explanation="Ping Google",
            safety_level=SafetyLevel.SAFE
        ),
        Command(
            command="sudo rm -rf /tmp/test",
            explanation="Remove test directory",
            safety_level=SafetyLevel.CAUTION,
            requires_sudo=True
        )
    ]


@pytest.fixture
def mock_os_info():
    """Mock OS information."""
    from pilotcmd.os_utils.detector import OSInfo, OSType
    
    return OSInfo(
        type=OSType.LINUX,
        name="Linux",
        version="5.4.0",
        architecture="x86_64",
        shell="bash",
        package_manager="apt"
    )
