"""
main_gui.py: Modern GUI Application for AI Voice Assistant.

A customtkinter-based voice assistant with visual feedback and Gemini AI integration.
Features real-time status indicators and responsive UI.
"""

import os
import threading
import time
from pathlib import Path
import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


class VoiceAssistantGUI(ctk.CTk):
    """
    Modern GUI-based AI Voice Assistant.
    
    Features:
    - Always-on-top window
    - Real-time visual feedback (Red/Blue/Green status)
    - Threaded processing for responsive UI
    - Gemini AI with optimized settings for accuracy
    - Conversation logging
    """
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("AI Voice Assistant")
        self.geometry("500x700")
        
        # Always on top
        self.attributes("-topmost", True)
        
        # Dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # State tracking
        self.is_listening = False
        self.processing_thread = None
        
        # Build GUI first (creates conversation_log widget)
        self._build_gui()
        
        # Initialize AI components after GUI is built
        self._initialize_ai()
        
        # Log initial messages (now conversation_log exists)
        self._log_message("System", "AI Voice Assistant Ready!")
        self._log_message("System", "Click the microphone to start speaking...")
    
    def _initialize_ai(self):
        """Initialize AI engines (Gemini, Speech Recognition, TTS)."""
        try:
            # Configure Gemini API
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "API Key not found. Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable."
                )
            
            # Configure with the stable API
            genai.configure(api_key=api_key)
            
            # Model configuration
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            system_instruction = (
                "You are a helpful and friendly AI voice assistant. "
                "Provide clear, concise, and accurate responses. "
                "Keep your answers conversational since they will be spoken aloud. "
                "Be helpful and engaging."
            )
            
            # Initialize model with stable gemini-2.5-flash
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config=generation_config,
                system_instruction=system_instruction
            )
            
            # Initialize speech recognition
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            
            # Initialize TTS engine
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            
            # Get available voices and set a good one
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to find a female voice (usually index 1 on Windows)
                self.tts_engine.setProperty('voice', voices[0].id if len(voices) > 1 else voices[0].id)
            
            self._log_message("System", "✅ AI engines initialized successfully")
        
        except Exception as e:
            self._log_message("System", f"❌ Initialization error: {e}")
            raise
    
    def _build_gui(self):
        """Build the GUI interface."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎤 AI Voice Assistant",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 20))
        
        # Microphone button container (for circular effect)
        mic_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        mic_container.pack(pady=30)
        
        # Large circular microphone button
        self.mic_button = ctk.CTkButton(
            mic_container,
            text="🎤",
            font=ctk.CTkFont(size=72),
            width=200,
            height=200,
            corner_radius=100,  # Makes it circular
            border_width=5,
            border_color="gray",
            fg_color="#1f1f1f",
            hover_color="#2f2f2f",
            command=self._on_mic_button_click
        )
        self.mic_button.pack()
        
        # Instructions
        instructions = ctk.CTkLabel(
            main_frame,
            text="Click microphone to speak",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        instructions.pack(pady=(10, 20))
        
        # Conversation log label
        log_label = ctk.CTkLabel(
            main_frame,
            text="Conversation Log:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.pack(pady=(10, 5), anchor="w")
        
        # Scrolling conversation log
        self.conversation_log = ctk.CTkTextbox(
            main_frame,
            height=250,
            font=ctk.CTkFont(size=12),
            wrap="word",
            state="disabled"  # Read-only
        )
        self.conversation_log.pack(fill="both", expand=True, pady=(0, 10))
        
        # Clear log button
        clear_button = ctk.CTkButton(
            main_frame,
            text="Clear Log",
            width=100,
            height=30,
            command=self._clear_log
        )
        clear_button.pack()
    
    def _set_status(self, status: str, color: str = "gray"):
        """Update status label."""
        self.status_label.configure(text=status, text_color=color)
    
    def _set_mic_border_color(self, color: str):
        """Change microphone button border color for visual feedback."""
        self.mic_button.configure(border_color=color)
    
    def _log_message(self, speaker: str, message: str):
        """Add message to conversation log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.conversation_log.configure(state="normal")
        self.conversation_log.insert(
            "end",
            f"[{timestamp}] {speaker}: {message}\n\n"
        )
        self.conversation_log.see("end")  # Auto-scroll to bottom
        self.conversation_log.configure(state="disabled")
    
    def _clear_log(self):
        """Clear the conversation log."""
        self.conversation_log.configure(state="normal")
        self.conversation_log.delete("1.0", "end")
        self.conversation_log.configure(state="disabled")
        self._log_message("System", "Log cleared")
    
    def _on_mic_button_click(self):
        """Handle microphone button click."""
        if self.is_listening:
            return  # Already processing
        
        # Start processing in separate thread
        self.processing_thread = threading.Thread(target=self._process_voice_input, daemon=True)
        self.processing_thread.start()
    
    def _process_voice_input(self):
        """
        Main processing pipeline (runs in separate thread).
        
        Flow:
        1. Listen (RED border)
        2. Transcribe & Think with Gemini (BLUE border)
        3. Speak response (GREEN border)
        """
        self.is_listening = True
        
        try:
            # PHASE 1: LISTENING (RED)
            self._set_mic_border_color("red")
            self._set_status("🔴 Listening...", "red")
            
            user_text = self._listen_to_microphone()
            
            if not user_text:
                self._set_mic_border_color("gray")
                self._set_status("Ready", "gray")
                self.is_listening = False
                return
            
            # Log user input
            self._log_message("You", user_text)
            
            # Check for exit commands
            if any(word in user_text.lower() for word in ['exit', 'quit', 'goodbye', 'bye']):
                response = "Goodbye! It was great talking with you."
                self._log_message("Assistant", response)
                self._set_mic_border_color("green")
                self._set_status("🟢 Speaking...", "green")
                self._speak(response)
                
                # Shut down after goodbye
                self.after(2000, self.quit)
                return
            
            # PHASE 2: THINKING (BLUE)
            self._set_mic_border_color("blue")
            self._set_status("🔵 Processing with Gemini...", "blue")
            
            response_text = self._get_gemini_response(user_text)
            
            # Log assistant response
            self._log_message("Assistant", response_text)
            
            # PHASE 3: SPEAKING (GREEN)
            self._set_mic_border_color("green")
            self._set_status("🟢 Speaking...", "green")
            
            self._speak(response_text)
            
            # Reset to ready state
            self._set_mic_border_color("gray")
            self._set_status("Ready", "gray")
        
        except Exception as e:
            self._log_message("System", f"❌ Error: {str(e)}")
            self._set_mic_border_color("gray")
            self._set_status("Error - Ready", "orange")
        
        finally:
            self.is_listening = False
    
    def _listen_to_microphone(self) -> str:
        """
        Listen to microphone and return transcribed text.
        
        Returns:
            str: Transcribed text or empty string if failed
        """
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            # Transcribe using Google Speech Recognition
            text = self.recognizer.recognize_google(audio)
            return text.strip()
        
        except sr.UnknownValueError:
            self._log_message("System", "⚠️ Could not understand audio")
            return ""
        
        except sr.RequestError as e:
            self._log_message("System", f"⚠️ Speech recognition error: {e}")
            return ""
        
        except sr.WaitTimeoutError:
            self._log_message("System", "⚠️ No speech detected (timeout)")
            return ""
        
        except Exception as e:
            self._log_message("System", f"⚠️ Microphone error: {e}")
            return ""
    
    def _get_gemini_response(self, user_input: str) -> str:
        """
        Get response from Gemini AI.
        
        Args:
            user_input (str): User's query
        
        Returns:
            str: AI's response
        """
        try:
            # Generate response with Gemini
            response = self.model.generate_content(user_input)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
        
        except Exception as e:
            error_msg = str(e)
            self._log_message("System", f"❌ Gemini API error: {error_msg[:100]}")
            
            # User-friendly error messages
            if "quota" in error_msg.lower() or "429" in error_msg:
                return "Sorry, the API quota has been exceeded. Please try again later or use a different API key."
            elif "api key" in error_msg.lower():
                return "API key error. Please check your GEMINI_API_KEY in the .env file."
            else:
                return "I encountered an error processing your request. Please try again."
    
    def _speak(self, text: str):
        """
        Convert text to speech and play it.
        
        Args:
            text (str): Text to speak
        """
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        except Exception as e:
            self._log_message("System", f"❌ TTS error: {e}")


def main():
    """Entry point for the GUI application."""
    try:
        app = VoiceAssistantGUI()
        app.mainloop()
    
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease set your API key:")
        print("  PowerShell: $env:GEMINI_API_KEY='AIzaSyCSK2suP0DzwcQ7sGZKYW3JwG7XQomawP8'")
        print("  Or add to .env file: GEMINI_API_KEY=your-key")
        print("\nGet your key from: https://aistudio.google.com/app/apikey\n")
    
    except Exception as e:
        print(f"\n❌ Fatal Error: {e}\n")


if __name__ == "__main__":
    main()
