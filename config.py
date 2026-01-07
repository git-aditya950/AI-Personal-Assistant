"""
config.py: Configuration management for the AI Voice Assistant.

Loads environment variables and provides configuration defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Configuration class for the Voice Assistant."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # TTS Configuration
    TTS_VOICE: str = os.getenv("TTS_VOICE", "en-US-AriaNeural")
    
    # Speech Recognition Configuration
    ENERGY_THRESHOLD: int = int(os.getenv("ENERGY_THRESHOLD", "4000"))
    LISTEN_TIMEOUT: float = float(os.getenv("LISTEN_TIMEOUT", "5.0"))
    PHRASE_TIME_LIMIT: float = float(os.getenv("PHRASE_TIME_LIMIT", "10.0"))
    
    # Agent Configuration
    MAX_CONVERSATION_HISTORY: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "20"))
    MAX_AGENT_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "5"))
    
    # System Prompt
    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are a helpful, friendly AI voice assistant. "
        "You can have natural conversations and use available tools when needed. "
        "Keep your responses concise and conversational since they will be spoken aloud. "
        "When using tools, explain what you're doing in a natural way. "
        "Today's date is January 7, 2026."
    )
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.
        
        Returns:
            bool: True if configuration is valid
        
        Raises:
            ValueError: If required configuration is missing
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required. "
                "Set it in your environment or create a .env file."
            )
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (safely)."""
        print("\n" + "="*60)
        print("Current Configuration:")
        print("="*60)
        print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"TTS Voice: {cls.TTS_VOICE}")
        print(f"Energy Threshold: {cls.ENERGY_THRESHOLD}")
        print(f"Listen Timeout: {cls.LISTEN_TIMEOUT}s")
        print(f"Max Conversation History: {cls.MAX_CONVERSATION_HISTORY}")
        print(f"API Key: {'✓ Set' if cls.OPENAI_API_KEY else '✗ Not Set'}")
        print("="*60 + "\n")
