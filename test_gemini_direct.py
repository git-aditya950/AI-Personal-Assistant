"""
Quick test script to verify Gemini API is working correctly.
Run this to test the AI response without the GUI.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini():
    """Test Gemini API with the configured key."""
    print("=" * 60)
    print("Testing Gemini API")
    print("=" * 60)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: No API key found!")
        print("Set GEMINI_API_KEY in your .env file")
        return False
    
    print(f"✅ API key found: {api_key[:15]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create model
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        print("✅ Model initialized: gemini-2.5-flash")
        print("\nTesting responses...\n")
        
        # Test queries
        test_queries = [
            "Say hello in one sentence.",
            "What is 25 + 17?",
            "Tell me a very short joke."
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {query}")
            print("-" * 60)
            
            try:
                response = model.generate_content(query)
                if response and response.text:
                    print(f"✅ Response: {response.text.strip()}")
                else:
                    print("❌ No response text received")
            except Exception as e:
                print(f"❌ Error: {str(e)[:100]}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("Your Gemini API is working correctly!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_gemini()
