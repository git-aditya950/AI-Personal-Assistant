"""
main.py: Async main loop for the LLM-powered Voice Assistant Agent.

Orchestrates the complete voice interaction cycle:
1. Record audio from microphone
2. Transcribe using OpenAI Whisper API
3. Process with VoiceAgent (LLM + function calling)
4. Synthesize response using edge-tts
5. Play audio response

Everything is asynchronous for maximum performance.
"""

import asyncio
import os
import logging
import tempfile
import wave
from pathlib import Path
from typing import Optional

import speech_recognition as sr
import edge_tts
from openai import AsyncOpenAI
import pygame

from agent import VoiceAgent


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VoiceAssistant:
    """
    Async voice assistant that integrates:
    - Speech Recognition (microphone wrapper)
    - OpenAI Whisper API (transcription)
    - VoiceAgent (LLM with function calling)
    - edge-tts (text-to-speech synthesis)
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        tts_voice: str = "en-US-AriaNeural",
        temp_dir: Optional[str] = None
    ):
        """
        Initialize the Voice Assistant.
        
        Args:
            openai_api_key (str, optional): OpenAI API key
            tts_voice (str): edge-tts voice name
            temp_dir (str, optional): Directory for temporary audio files
        """
        # Initialize OpenAI client for Whisper
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env variable.")
        
        self.openai_client = AsyncOpenAI(api_key=api_key)
        
        # Initialize the LLM agent
        self.agent = VoiceAgent(api_key=api_key)
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        
        # TTS setup
        self.tts_voice = tts_voice
        
        # Temp directory for audio files
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        self.running = False
        
        logger.info("VoiceAssistant initialized")
    
    async def listen_for_audio(self, timeout: float = 5.0) -> Optional[bytes]:
        """
        Listen for audio from the microphone using speech_recognition.
        This is a blocking operation wrapped in asyncio.
        
        Args:
            timeout (float): Timeout in seconds
        
        Returns:
            bytes: Audio data in WAV format, or None if failed
        """
        logger.info("Listening for audio...")
        
        try:
            # Run blocking operation in executor
            loop = asyncio.get_event_loop()
            audio_data = await loop.run_in_executor(
                None,
                self._record_audio_sync,
                timeout
            )
            
            if audio_data:
                logger.info(f"Audio captured: {len(audio_data)} bytes")
            return audio_data
        
        except Exception as e:
            logger.error(f"Error capturing audio: {e}")
            return None
    
    def _record_audio_sync(self, timeout: float) -> Optional[bytes]:
        """
        Synchronous audio recording (runs in executor).
        
        Args:
            timeout (float): Timeout in seconds
        
        Returns:
            bytes: Audio data or None
        """
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
            
            # Get WAV data
            return audio.get_wav_data()
        
        except sr.WaitTimeoutError:
            logger.debug("Listening timeout - no speech detected")
            return None
        except Exception as e:
            logger.error(f"Recording error: {e}")
            return None
    
    async def transcribe_audio_whisper(self, audio_data: bytes) -> Optional[str]:
        """
        Transcribe audio using OpenAI's Whisper API.
        
        Args:
            audio_data (bytes): Audio data in WAV format
        
        Returns:
            str: Transcribed text, or None if failed
        """
        logger.info("Transcribing audio with Whisper API...")
        
        try:
            # Save audio to temporary file
            temp_audio_path = self.temp_dir / "temp_audio.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(audio_data)
            
            # Call Whisper API
            with open(temp_audio_path, "rb") as audio_file:
                transcript = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # You can make this configurable
                )
            
            transcribed_text = transcript.text.strip()
            logger.info(f"Transcribed: {transcribed_text}")
            
            # Clean up temp file
            temp_audio_path.unlink(missing_ok=True)
            
            return transcribed_text if transcribed_text else None
        
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return None
    
    async def synthesize_speech(self, text: str) -> Optional[Path]:
        """
        Synthesize speech from text using edge-tts.
        
        Args:
            text (str): Text to synthesize
        
        Returns:
            Path: Path to generated audio file, or None if failed
        """
        logger.info(f"Synthesizing speech: {text[:50]}...")
        
        try:
            output_path = self.temp_dir / "response.mp3"
            
            # Use edge-tts to synthesize
            communicate = edge_tts.Communicate(text, self.tts_voice)
            await communicate.save(str(output_path))
            
            logger.info(f"Speech synthesized: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    async def play_audio(self, audio_path: Path):
        """
        Play audio file asynchronously using pygame.
        
        Args:
            audio_path (Path): Path to audio file
        """
        try:
            logger.info(f"Playing audio: {audio_path}")
            
            # Run pygame audio in executor (it's blocking)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._play_audio_sync, str(audio_path))
            
            # Brief delay to ensure file is released
            await asyncio.sleep(0.1)
            
            # Clean up
            audio_path.unlink(missing_ok=True)
        
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def _play_audio_sync(self, audio_path: str):
        """
        Synchronous audio playback using pygame.
        
        Args:
            audio_path (str): Path to audio file
        """
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Unload to release the file
            pygame.mixer.music.unload()
        
        except Exception as e:
            logger.error(f"Pygame playback error: {e}")
    
    async def speak(self, text: str):
        """
        Complete text-to-speech pipeline: synthesize and play.
        
        Args:
            text (str): Text to speak
        """
        audio_path = await self.synthesize_speech(text)
        if audio_path:
            await self.play_audio(audio_path)
    
    async def run(self):
        """
        Main async event loop for the voice assistant.
        
        Flow:
        1. Listen for audio
        2. Transcribe with Whisper
        3. Process with LLM agent (with function calling)
        4. Speak response
        """
        self.running = True
        
        # Welcome message
        welcome_msg = "Hello! I'm your AI voice assistant. I'm ready to help!"
        logger.info(welcome_msg)
        await self.speak(welcome_msg)
        
        print("\n" + "="*70)
        print("🎙️  AI Voice Assistant is Running (Async + LLM + Function Calling)")
        print("="*70)
        print("\nSpeak naturally! I can:")
        print("  • Answer questions and chat")
        print("  • Tell you the time and date")
        print("  • Get weather information (dummy data)")
        print("  • Search the web (dummy data)")
        print("  • Perform calculations")
        print("  • Get system information")
        print("\nSay 'exit', 'quit', or 'goodbye' to stop.")
        print("="*70 + "\n")
        
        while self.running:
            try:
                # Step 1: Listen for audio
                print("🎤 Listening...")
                audio_data = await self.listen_for_audio(timeout=1.0)
                
                if not audio_data:
                    await asyncio.sleep(0.1)
                    continue
                
                # Step 2: Transcribe with Whisper
                user_text = await self.transcribe_audio_whisper(audio_data)
                
                if not user_text:
                    continue
                
                print(f"👤 You: {user_text}")
                
                # Check for exit commands
                if any(word in user_text.lower() for word in ['exit', 'quit', 'goodbye', 'bye bye']):
                    goodbye_msg = "Goodbye! It was great talking with you."
                    print(f"🤖 Assistant: {goodbye_msg}")
                    await self.speak(goodbye_msg)
                    self.running = False
                    break
                
                # Step 3: Process with LLM agent (the "brain")
                # This handles function calling automatically
                print("🧠 Processing with LLM agent...")
                response_text = await self.agent.process_user_input(user_text)
                
                print(f"🤖 Assistant: {response_text}")
                
                # Step 4: Speak the response
                await self.speak(response_text)
            
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received")
                break
            
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                error_msg = "I encountered an error. Let me continue listening."
                await self.speak(error_msg)
        
        print("\n" + "="*70)
        print("AI Voice Assistant has been shut down.")
        print("="*70 + "\n")
        logger.info("Assistant shutdown complete")
    
    async def interactive_mode(self):
        """
        Run in text-based interactive mode (no voice I/O).
        Useful for testing without microphone/speakers.
        """
        self.running = True
        
        print("\n" + "="*70)
        print("🤖 AI Voice Assistant (Text Mode - No Voice I/O)")
        print("="*70)
        print("\nType naturally! I can:")
        print("  • Answer questions and chat")
        print("  • Tell you the time and date")
        print("  • Get weather information (dummy data)")
        print("  • Search the web (dummy data)")
        print("  • Perform calculations")
        print("  • Get system information")
        print("\nType 'exit', 'quit', or 'goodbye' to stop.")
        print("="*70 + "\n")
        
        while self.running:
            try:
                # Get text input
                user_text = input("You: ").strip()
                
                if not user_text:
                    continue
                
                # Check for exit commands
                if any(word in user_text.lower() for word in ['exit', 'quit', 'goodbye', 'bye']):
                    print("Assistant: Goodbye! It was great talking with you.")
                    self.running = False
                    break
                
                # Process with LLM agent
                response_text = await self.agent.process_user_input(user_text)
                print(f"Assistant: {response_text}\n")
            
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received")
                break
            
            except Exception as e:
                logger.error(f"Error in interactive loop: {e}")
                print(f"Error: {e}\n")
        
        print("\nAI Voice Assistant has been shut down.\n")


async def main():
    """Entry point for the async voice assistant."""
    import sys
    
    try:
        assistant = VoiceAssistant()
        
        # Check for command-line arguments
        if len(sys.argv) > 1 and sys.argv[1].lower() == '--interactive':
            await assistant.interactive_mode()
        else:
            await assistant.run()
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Error: {e}")
        print("Please set your OPENAI_API_KEY environment variable.\n")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}\n")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
