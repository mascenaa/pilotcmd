#!/usr/bin/env python3
"""
Setup script for PilotCmd development.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("🚁 PilotCmd Development Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    commands = [
        (f"{pip_cmd} install --upgrade pip", "Upgrading pip"),
        (f"{pip_cmd} install -e .", "Installing PilotCmd in development mode"),
        (f"{pip_cmd} install -e .[dev]", "Installing development dependencies"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print(f"⚠️  Failed to {desc.lower()}, but continuing...")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    if os.name == 'nt':
        print("1. Activate virtual environment: venv\\Scripts\\activate")
    else:
        print("1. Activate virtual environment: source venv/bin/activate")
    
    print("2. Set your OpenAI API key:")
    print("   export OPENAI_API_KEY='your-key-here'")
    print("   # or")
    print("   pilotcmd config --api-key your-key-here")
    print("\n3. Test the installation:")
    print("   pilotcmd \"list files in current directory\" --dry-run")
    print("\n4. Run tests:")
    print("   pytest tests/")


if __name__ == "__main__":
    main()
