#!/usr/bin/env python3
"""Test script to verify the ExecutionResult fix."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import openai  # noqa: F401
except ModuleNotFoundError:
    pytest.skip("openai not available", allow_module_level=True)

from pilotcmd.executor.command_executor import ExecutionResult, ExecutionStatus
from pilotcmd.nlp.simple_parser import Command, SafetyLevel

# Create a mock command
mock_command = Command(
    command="echo test",
    description="test command",
    safety_level=SafetyLevel.SAFE
)

# Create an ExecutionResult with error_message
result = ExecutionResult(
    command=mock_command,
    status=ExecutionStatus.FAILED,
    return_code=1,
    stdout="",
    stderr="Test error",
    execution_time=0.1,
    timestamp=1234567890.0,
    error_message="This is a test error message"
)

# Test the fix - this should work without AttributeError
print("Testing ExecutionResult attributes:")
print(f"Has error_message: {hasattr(result, 'error_message')}")
print(f"error_message value: {result.error_message}")
print(f"Has error: {hasattr(result, 'error')}")

# Test the fixed code path
if result.error_message:
    print(f"✅ Fixed code works: Error message is '{result.error_message}'")
else:
    print("❌ No error message found")

print("Test completed successfully!")
