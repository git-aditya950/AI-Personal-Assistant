"""
main.py: Main orchestration module for the AI Personal Assistant.

Handles the core cycle: Listen -> Understand -> Act -> Respond
Manages speech recognition and text-to-speech interactions.
"""

import speech_recognition as sr
import pyttsx3
from typing import Optional
import logging

from nlu_engine import understand
from skills import execute_skill, SkillNotImplementedError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIAssistant:
    """
    Main AI Personal Assistant class.
    Orchestrates the listen -> understand -> act -> respond cycle.
    """
    
    def __init__(self):
        """Initialize the AI Assistant with speech recognition and TTS engines."""
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        
        # Configure TTS engine
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        
        self.running = False
        logger.info("AI Assistant initialized successfully")
    
    def speak(self, text: str):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to speak
        """
        logger.info(f"Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def listen(self, timeout: float = 5.0, phrase_time_limit: float = None) -> Optional[str]:
        """
        Listen for user input from the microphone.
        
        Args:
            timeout (float): Time in seconds to wait for sound
            phrase_time_limit (float): Max time for a phrase
        
        Returns:
            str: Recognized text, or None if recognition failed
        """
        try:
            with sr.Microphone() as source:
                logger.info("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            logger.info("Audio captured, recognizing...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"Recognized: {text}")
            return text
        
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            self.speak("Sorry, I didn't catch that. Could you repeat?")
            return None
        
        except sr.RequestError as e:
            logger.error(f"Speech recognition error: {e}")
            self.speak("Sorry, I'm having trouble with the speech recognition service.")
            return None
        
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout - no speech detected")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error during listening: {e}")
            self.speak("An unexpected error occurred.")
            return None
    
    def process_input(self, user_input: str) -> Optional[str]:
        """
        Process user input through NLU and execute the appropriate skill.
        
        Args:
            user_input (str): User's spoken or typed input
        
        Returns:
            str: Response to the user, or None if processing failed
        """
        try:
            # Understand the user's intent
            logger.info(f"Processing input: {user_input}")
            intent = understand(user_input)
            logger.info(f"Detected intent: {intent}")
            
            # Execute the skill associated with the intent
            response = execute_skill(intent.name, intent.entities)
            logger.info(f"Skill response: {response}")
            return response
        
        except SkillNotImplementedError as e:
            logger.warning(f"Skill not implemented: {e}")
            response = f"That feature is not yet available. {str(e)}"
            return response
        
        except KeyError as e:
            logger.error(f"Unknown intent: {e}")
            response = "I'm not sure how to help with that. Could you try asking something else?"
            return response
        
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            response = "An error occurred while processing your request."
            return response
    
    def run(self):
        """
        Main loop: Listen -> Understand -> Act -> Respond.
        Runs continuously until interrupted by the user.
        """
        self.running = True
        self.speak("Hello! I'm your AI Personal Assistant. I'm ready to help!")
        logger.info("Assistant started and ready for commands")
        
        print("\n" + "="*60)
        print("AI Personal Assistant is running")
        print("Say commands like: 'What time is it?', 'What's the date?', 'Hello!'")
        print("Say 'exit' or 'quit' to stop")
        print("="*60 + "\n")
        
        while self.running:
            try:
                # Listen for user input
                user_input = self.listen(timeout=1.0, phrase_time_limit=5.0)
                
                if user_input is None:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye', 'stop']:
                    self.speak("Goodbye! Thank you for using me.")
                    logger.info("User requested exit")
                    self.running = False
                    break
                
                # Process the input and get a response
                response = self.process_input(user_input)
                
                if response:
                    self.speak(response)
            
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received")
                self.speak("Shutting down. Goodbye!")
                self.running = False
                break
            
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                self.speak("An unexpected error occurred. Let me continue listening.")
        
        print("\nAI Assistant has been shut down.\n")
        logger.info("Assistant shutdown complete")
    
    def interactive_mode(self):
        """
        Run in interactive (text input) mode instead of speech recognition.
        Useful for testing and debugging.
        """
        self.running = True
        self.speak("Hello! I'm your AI Personal Assistant. I'm ready to help!")
        logger.info("Assistant started in interactive mode")
        
        print("\n" + "="*60)
        print("AI Personal Assistant (Interactive Mode)")
        print("Type commands like: 'What time is it?', 'What's the date?', 'Hello!'")
        print("Type 'exit' or 'quit' to stop")
        print("="*60 + "\n")
        
        while self.running:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye', 'stop']:
                    self.speak("Goodbye! Thank you for using me.")
                    logger.info("User requested exit")
                    self.running = False
                    break
                
                # Process the input and get a response
                response = self.process_input(user_input)
                
                if response:
                    print(f"Assistant: {response}")
                    self.speak(response)
            
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received")
                self.speak("Shutting down. Goodbye!")
                self.running = False
                break
            
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                print(f"Error: {e}")
        
        print("\nAI Assistant has been shut down.\n")
        logger.info("Assistant shutdown complete")


def main():
    """Entry point for the AI Personal Assistant."""
    import sys
    
    assistant = AIAssistant()
    
    # Check for command-line arguments
    if len(sys.argv) > 1 and sys.argv[1].lower() == '--interactive':
        assistant.interactive_mode()
    else:
        assistant.run()


if __name__ == "__main__":
    main()
