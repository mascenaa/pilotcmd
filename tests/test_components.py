#!/usr/bin/env python3
"""
Quick test script for PilotCmd functionality.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_os_detection():
    """Test OS detection."""
    print("🔍 Testing OS Detection...")
    try:
        from pilotcmd.os_utils.detector import OSDetector
        
        detector = OSDetector()
        os_info = detector.detect()
        
        print(f"✅ OS Type: {os_info.type.value}")
        print(f"✅ OS Name: {os_info.name}")
        print(f"✅ Shell: {os_info.shell}")
        print(f"✅ Package Manager: {os_info.package_manager}")
        
        return True
    except Exception as e:
        print(f"❌ OS Detection failed: {e}")
        return False

def test_simple_parser():
    """Test simple parser."""
    print("\n🔍 Testing Simple Parser...")
    try:
        from pilotcmd.os_utils.detector import OSDetector
        from pilotcmd.nlp.simple_parser import SimpleParser
        
        detector = OSDetector()
        os_info = detector.detect()
        parser = SimpleParser(os_info)
        
        test_prompts = [
            "list files in current directory",
            "show current directory", 
            "ping google.com",
            "find Python files"
        ]
        
        for prompt in test_prompts:
            commands = parser.parse(prompt)
            if commands:
                print(f"✅ '{prompt}' → {commands[0].command}")
            else:
                print(f"⚠️  '{prompt}' → No command generated")
        
        return True
    except ImportError as e:
        print(f"❌ Simple Parser import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Simple Parser failed: {e}")
        return False

def test_context_manager():
    """Test context manager."""
    print("\n🔍 Testing Context Manager...")
    try:
        from pilotcmd.context_db.manager import ContextManager
        import tempfile
        import os
        
        # Use a temporary file instead of :memory: for testing
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            manager = ContextManager(db_path=db_path)
            stats = manager.get_stats()
            
            print(f"✅ Context Manager initialized")
            print(f"✅ Total commands: {stats['total_commands']}")
            
            return True
        finally:
            # Cleanup - ignore errors on Windows
            try:
                if os.path.exists(db_path):
                    os.unlink(db_path)
            except:
                pass  # Ignore cleanup errors
                
    except Exception as e:
        print(f"❌ Context Manager failed: {e}")
        return False

def test_config_manager():
    """Test config manager."""
    print("\n🔍 Testing Config Manager...")
    try:
        from pilotcmd.config.manager import ConfigManager
        import tempfile
        
        # Use a temporary config file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            config_path = f.name
        
        manager = ConfigManager(config_path)
        config = manager.get_config()
        
        print(f"✅ Config Manager initialized")
        print(f"✅ Default model: {config.default_model}")
        print(f"✅ Timeout: {config.default_timeout}")
        
        # Cleanup
        os.unlink(config_path)
        
        return True
    except Exception as e:
        print(f"❌ Config Manager failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚁 PilotCmd Component Tests")
    print("=" * 40)
    
    tests = [
        test_os_detection,
        test_simple_parser,
        test_context_manager,
        test_config_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PilotCmd components are working.")
        print("\nNext steps:")
        print("1. Set up your AI model (OpenAI API key or Ollama)")
        print("2. Try: python -m pilotcmd 'list files' --dry-run")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
