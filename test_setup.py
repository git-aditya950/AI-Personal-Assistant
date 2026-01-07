"""
test_setup.py: Test script to verify installation and setup.

Run this script to check if all dependencies are properly installed
before running the main assistant.
"""

import sys
import importlib


def check_module(module_name, package_name=None):
    """
    Check if a module can be imported.
    
    Args:
        module_name (str): Name of the module to import
        package_name (str, optional): Display name for the package
    
    Returns:
        bool: True if module is available
    """
    display_name = package_name or module_name
    try:
        importlib.import_module(module_name)
        print(f"✅ {display_name} - OK")
        return True
    except ImportError as e:
        print(f"❌ {display_name} - MISSING")
        print(f"   Error: {e}")
        return False


def check_environment():
    """Check environment variables."""
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OPENAI_API_KEY - SET (length: {len(api_key)} chars)")
        return True
    else:
        print("⚠️  OPENAI_API_KEY - NOT SET")
        print("   Set it with: $env:OPENAI_API_KEY='your-api-key'")
        return False


def test_imports():
    """Test all required imports."""
    print("\n" + "="*60)
    print("Testing Dependencies")
    print("="*60 + "\n")
    
    modules = [
        ("speech_recognition", "SpeechRecognition"),
        ("edge_tts", "edge-tts"),
        ("openai", "OpenAI SDK"),
        ("pygame", "Pygame"),
        ("dotenv", "python-dotenv"),
        ("aiofiles", "aiofiles"),
    ]
    
    results = []
    for module_name, display_name in modules:
        results.append(check_module(module_name, display_name))
    
    print("\n" + "="*60)
    print("Testing Environment Variables")
    print("="*60 + "\n")
    
    api_key_set = check_environment()
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60 + "\n")
    
    if all(results):
        print("✅ All dependencies are installed!")
    else:
        print("❌ Some dependencies are missing.")
        print("   Run: pip install -r requirements.txt")
    
    if api_key_set:
        print("✅ API key is configured!")
        print("\n🎉 You're ready to run the assistant!")
        print("\nRun: python main_async.py --interactive")
    else:
        print("⚠️  API key is not set.")
        print("\nTo set your API key:")
        print("  PowerShell: $env:OPENAI_API_KEY='sk-your-key'")
        print("  Or create a .env file with: OPENAI_API_KEY=sk-your-key")
    
    print("\n" + "="*60 + "\n")
    
    return all(results) and api_key_set


def test_pyaudio():
    """Test PyAudio (microphone support)."""
    print("\n" + "="*60)
    print("Testing Microphone Support (PyAudio)")
    print("="*60 + "\n")
    
    try:
        import pyaudio
        print("✅ PyAudio is installed")
        
        # Try to initialize
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        print(f"✅ Found {device_count} audio device(s)")
        
        # List input devices
        print("\nAvailable microphones:")
        for i in range(device_count):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                print(f"  - {info['name']}")
        
        p.terminate()
        return True
    
    except ImportError:
        print("❌ PyAudio is not installed")
        print("\nInstall PyAudio:")
        print("  pip install PyAudio")
        return False
    
    except Exception as e:
        print(f"⚠️  PyAudio error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AI Voice Assistant - Setup Verification")
    print("="*60 + "\n")
    
    # Test imports
    imports_ok = test_imports()
    
    # Test PyAudio
    pyaudio_ok = test_pyaudio()
    
    print("\n" + "="*60)
    print("Final Status")
    print("="*60 + "\n")
    
    if imports_ok:
        print("✅ READY TO RUN!")
        print("\nQuick Start:")
        print("  1. python main_async.py --interactive  (text mode)")
        print("  2. python main_async.py                (voice mode)")
    else:
        print("❌ NOT READY")
        print("\nPlease fix the issues above and run this test again.")
    
    print("\n")


if __name__ == "__main__":
    main()
