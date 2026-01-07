"""
demo_offline.py: Offline demo to test the system without OpenAI API.

This script tests the basic components without requiring an API key:
- Microphone recording
- Audio playback
- Tool execution
- Agent workflow (mocked)
"""

import asyncio
import logging
from pathlib import Path
import tempfile

import speech_recognition as sr
import edge_tts
import pygame

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_microphone():
    """Test microphone recording."""
    print("\n" + "="*60)
    print("TEST 1: Microphone Recording")
    print("="*60)
    
    try:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Adjusting for ambient noise... (please wait)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("✅ Microphone is working!")
            print("🎤 Say something now! (you have 3 seconds)")
            
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            print(f"✅ Recorded audio: {len(audio.get_wav_data())} bytes")
            return True
    
    except sr.WaitTimeoutError:
        print("⚠️  No speech detected (timeout)")
        return True  # Not an error, just no input
    
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False


async def test_tts():
    """Test text-to-speech."""
    print("\n" + "="*60)
    print("TEST 2: Text-to-Speech (edge-tts)")
    print("="*60)
    
    try:
        text = "Hello! This is a test of the text to speech system."
        print(f"📢 Synthesizing: '{text}'")
        
        temp_dir = Path(tempfile.gettempdir())
        output_path = temp_dir / "demo_tts.mp3"
        
        # Synthesize speech
        communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
        await communicate.save(str(output_path))
        
        print(f"✅ TTS file created: {output_path}")
        print(f"   File size: {output_path.stat().st_size} bytes")
        
        # Test playback
        print("🔊 Playing audio...")
        pygame.mixer.init()
        pygame.mixer.music.load(str(output_path))
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.unload()  # Release the file
        print("✅ Audio playback successful!")
        
        # Cleanup
        import time
        time.sleep(0.1)  # Brief pause to ensure file is released
        output_path.unlink(missing_ok=True)
        return True
    
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        return False


def test_tools():
    """Test tool execution (no API needed)."""
    print("\n" + "="*60)
    print("TEST 3: Tool Execution")
    print("="*60)
    
    try:
        from tools import ToolBox
        
        # Test time tool
        print("🔧 Testing: get_current_time()")
        result = ToolBox.get_current_time()
        print(f"   Result: {result}")
        
        # Test calculator
        print("🔧 Testing: calculate('10 * 5 + 3')")
        result = ToolBox.calculate("10 * 5 + 3")
        print(f"   Result: {result}")
        
        # Test system info
        print("🔧 Testing: get_system_info()")
        result = ToolBox.get_system_info()
        print(f"   Result: System = {result['system']}, Version = {result['release']}")
        
        print("✅ All tools working!")
        return True
    
    except Exception as e:
        print(f"❌ Tools test failed: {e}")
        return False


async def test_full_cycle():
    """Test the complete cycle without OpenAI API."""
    print("\n" + "="*60)
    print("TEST 4: Full Cycle Demo (Simulated)")
    print("="*60)
    
    try:
        print("This test simulates the full assistant cycle:")
        print("  1. User speaks → 2. Transcribe → 3. LLM → 4. Speak response")
        print("\nIn this demo, we'll use dummy text instead of real speech/LLM.")
        
        # Simulate user input
        user_text = "What time is it?"
        print(f"\n👤 [Simulated User]: {user_text}")
        
        # Execute tool directly (simulating what LLM would do)
        from tools import ToolBox
        response_data = ToolBox.get_current_time()
        response = f"The current time is {response_data['time']} on {response_data['day_of_week']}."
        print(f"🤖 [Simulated Assistant]: {response}")
        
        # Synthesize and play response
        print("🔊 Speaking response...")
        temp_dir = Path(tempfile.gettempdir())
        output_path = temp_dir / "demo_response.mp3"
        
        communicate = edge_tts.Communicate(response, "en-US-AriaNeural")
        await communicate.save(str(output_path))
        
        pygame.mixer.init()
        pygame.mixer.music.load(str(output_path))
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.unload()  # Release the file
        import time
        time.sleep(0.1)  # Brief pause to ensure file is released
        output_path.unlink(missing_ok=True)
        
        print("✅ Full cycle successful!")
        return True
    
    except Exception as e:
        print(f"❌ Full cycle test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🤖 AI Voice Assistant - Offline Demo")
    print("="*60)
    print("\nThis demo tests the system WITHOUT needing an OpenAI API key.")
    print("It verifies that all local components are working correctly.\n")
    
    results = []
    
    # Test 1: Microphone
    results.append(await test_microphone())
    
    # Test 2: TTS
    results.append(await test_tts())
    
    # Test 3: Tools
    results.append(test_tools())
    
    # Test 4: Full cycle
    results.append(await test_full_cycle())
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\n🎉 Your system is ready!")
        print("\nTo use the full AI assistant:")
        print("  1. Get an OpenAI API key from: https://platform.openai.com/api-keys")
        print("  2. Set it: $env:OPENAI_API_KEY='sk-your-key'")
        print("  3. Run: python main_async.py --interactive")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
        print("\nPlease check the errors above and ensure all dependencies are installed.")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
