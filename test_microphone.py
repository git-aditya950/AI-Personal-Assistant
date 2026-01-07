"""
Test microphone detection and settings.
Run this to diagnose audio detection issues.
"""

import speech_recognition as sr
import time

def test_microphone():
    """Test microphone detection and sensitivity."""
    print("=" * 60)
    print("Microphone Detection Test")
    print("=" * 60)
    
    recognizer = sr.Recognizer()
    
    # List available microphones
    print("\n📋 Available Microphones:")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  [{index}] {name}")
    
    print("\n" + "=" * 60)
    print("Testing with different sensitivity levels...")
    print("=" * 60)
    
    # Test with various energy thresholds
    test_thresholds = [100, 300, 500, 1000, 2000, 4000]
    
    for threshold in test_thresholds:
        print(f"\n🎤 Testing with threshold: {threshold}")
        print("Speak now for 3 seconds...")
        
        recognizer.energy_threshold = threshold
        recognizer.dynamic_energy_threshold = False
        
        try:
            with sr.Microphone() as source:
                # Quick ambient noise check
                print("  Adjusting for ambient noise (1 second)...")
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                print(f"  Adjusted threshold: {recognizer.energy_threshold}")
                
                # Listen
                print("  🔴 Listening...")
                audio = recognizer.listen(source, timeout=3.0, phrase_time_limit=5.0)
                
                print("  ✅ Audio detected!")
                
                # Try to recognize
                try:
                    text = recognizer.recognize_google(audio)
                    print(f"  ✅ Recognized: '{text}'")
                    print(f"\n🎉 SUCCESS! Threshold {threshold} works!")
                    print(f"Use this threshold in your settings.")
                    break
                except sr.UnknownValueError:
                    print("  ⚠️ Audio detected but couldn't understand speech")
                except sr.RequestError as e:
                    print(f"  ❌ Recognition error: {e}")
                    
        except sr.WaitTimeoutError:
            print("  ❌ No audio detected (timeout)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Recommendation:")
    print("=" * 60)
    print("1. Use threshold between 100-500 for quiet voices")
    print("2. Use threshold between 500-1000 for normal voices")
    print("3. Use threshold above 1000 for noisy environments")
    print("4. Enable 'Auto-adjust sensitivity' in settings")
    print("=" * 60)

if __name__ == "__main__":
    test_microphone()
