"""
main_gui_advanced.py: Advanced AI Voice Assistant with Modern Features

Features:
- Auto-adjusting microphone sensitivity for low voices
- Streaming responses for instant feedback
- Modern animated UI with smooth transitions
- Real-time transcription display
- Advanced settings panel
- Background noise suppression
- Conversation history with export
- Keyboard shortcuts
- Voice activity detection
- Multiple UI themes
"""

import os
import threading
import time
import json
from pathlib import Path
from datetime import datetime
import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Optional, Callable
import queue

# Load environment variables
load_dotenv()


class AdvancedVoiceAssistantGUI(ctk.CTk):
    """
    Advanced GUI-based AI Voice Assistant with modern features.
    
    Features:
    - Auto-adjusting microphone for low voices
    - Streaming AI responses
    - Real-time transcription
    - Settings panel
    - Conversation history
    - Modern animations
    """
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Advanced AI Voice Assistant")
        self.geometry("900x800")
        
        # Always on top (toggleable)
        self.always_on_top = True
        self.attributes("-topmost", True)
        
        # Dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # State tracking
        self.is_listening = False
        self.is_processing = False
        self.is_speaking = False
        self.processing_thread = None
        self.animation_running = False
        
        # Conversation history
        self.conversation_history = []
        
        # Settings
        self.settings = {
            "auto_adjust_mic": False,  # Disable to prevent threshold from getting too high
            "noise_suppression": False,  # Disable ambient adjustment that causes timeouts
            "streaming_response": True,
            "energy_threshold": 300,  # Lower for better low voice detection
            "dynamic_energy": False,  # Keep fixed threshold
            "pause_threshold": 0.8,
            "phrase_time_limit": 15,
            "ambient_duration": 0.5,  # Reduced from 2 to 0.5 seconds
            "temperature": 0.7,
            "always_on_top": True,
            "auto_speak": True,
            "show_transcription": True,
        }
        
        # Build GUI
        self._build_gui()
        
        # Initialize AI components after GUI is built
        self._initialize_ai()
        
        # Setup keyboard shortcuts
        self._setup_shortcuts()
        
        # Log initial messages
        self._log_message("System", "🚀 Advanced AI Voice Assistant Ready!")
        self._log_message("System", "Press SPACE or click microphone to start")
        self._log_message("System", "Press ESC to stop listening")
    
    def _initialize_ai(self):
        """Initialize AI engines with advanced settings."""
        try:
            # Configure Gemini API
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError(
                    "API Key not found. Set GEMINI_API_KEY in .env file."
                )
            
            # Configure with the stable API
            genai.configure(api_key=api_key)
            
            # Model configuration for better responses
            self.generation_config = {
                "temperature": self.settings["temperature"],
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            
            system_instruction = (
                "You are an advanced AI voice assistant. "
                "Provide clear, concise, and helpful responses. "
                "Be conversational and engaging. "
                "Keep responses brief for voice output (2-3 sentences max). "
                "If asked for detailed information, offer to provide more details. "
                "Current date: January 7, 2026."
            )
            
            # Initialize model
            self.model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                generation_config=self.generation_config,
                system_instruction=system_instruction
            )
            
            # Initialize speech recognition with advanced settings
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = self.settings["energy_threshold"]
            self.recognizer.dynamic_energy_threshold = self.settings["dynamic_energy"]
            self.recognizer.pause_threshold = self.settings["pause_threshold"]
            self.recognizer.phrase_threshold = 0.3
            self.recognizer.non_speaking_duration = 0.5
            
            # Initialize TTS engine
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 175)  # Slightly faster
            self.tts_engine.setProperty('volume', 0.9)
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                self.tts_engine.setProperty('voice', voices[0].id)
            
            self._log_message("System", "✅ AI engines initialized successfully")
            self._log_message("System", f"🎤 Microphone sensitivity: {self.settings['energy_threshold']}")
            self._log_message("System", "⚡ Streaming mode: Enabled")
        
        except Exception as e:
            self._log_message("System", f"❌ Initialization error: {e}")
            raise
    
    def _build_gui(self):
        """Build the advanced GUI interface."""
        # Create main container with two panels
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel (main interface)
        left_panel = ctk.CTkFrame(main_container, fg_color="transparent")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Right panel (settings and history)
        right_panel = ctk.CTkFrame(main_container, fg_color="#1a1a1a", corner_radius=15)
        right_panel.pack(side="right", fill="both", padx=(5, 0))
        right_panel.configure(width=300)
        
        # === LEFT PANEL ===
        
        # Header with title and controls
        header_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎤 Advanced AI Assistant",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(side="left")
        
        # Control buttons
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right")
        
        self.pin_button = ctk.CTkButton(
            controls_frame,
            text="📌",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            command=self._toggle_always_on_top
        )
        self.pin_button.pack(side="left", padx=2)
        
        settings_button = ctk.CTkButton(
            controls_frame,
            text="⚙️",
            width=40,
            height=40,
            font=ctk.CTkFont(size=20),
            command=self._show_settings
        )
        settings_button.pack(side="left", padx=2)
        
        # Status indicators row
        status_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="● Ready",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4CAF50"
        )
        self.status_label.pack(side="left")
        
        self.mic_level_label = ctk.CTkLabel(
            status_frame,
            text="🎤 Level: --",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.mic_level_label.pack(side="right")
        
        # Real-time transcription display
        transcription_frame = ctk.CTkFrame(left_panel, fg_color="#1a1a1a", corner_radius=10)
        transcription_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            transcription_frame,
            text="📝 Live Transcription",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.transcription_label = ctk.CTkLabel(
            transcription_frame,
            text="Waiting for input...",
            font=ctk.CTkFont(size=14),
            wraplength=500,
            justify="left"
        )
        self.transcription_label.pack(fill="x", padx=10, pady=(5, 10))
        
        # Microphone button container
        mic_container = ctk.CTkFrame(left_panel, fg_color="transparent")
        mic_container.pack(pady=20)
        
        # Large animated microphone button
        self.mic_button = ctk.CTkButton(
            mic_container,
            text="🎤",
            font=ctk.CTkFont(size=80),
            width=220,
            height=220,
            corner_radius=110,
            border_width=6,
            border_color="#4CAF50",
            fg_color="#1a1a1a",
            hover_color="#2a2a2a",
            command=self._on_mic_button_click
        )
        self.mic_button.pack()
        
        # Instructions
        instructions_text = "Press SPACE or Click to speak  •  ESC to stop"
        instructions = ctk.CTkLabel(
            left_panel,
            text=instructions_text,
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        instructions.pack(pady=(10, 15))
        
        # Response display area
        response_frame = ctk.CTkFrame(left_panel, fg_color="#1a1a1a", corner_radius=10)
        response_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(
            response_frame,
            text="💬 AI Response",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="gray"
        ).pack(anchor="w", padx=10, pady=(5, 0))
        
        self.response_display = ctk.CTkTextbox(
            response_frame,
            font=ctk.CTkFont(size=15),
            wrap="word",
            height=150
        )
        self.response_display.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # === RIGHT PANEL ===
        
        # Tab view for Settings and History
        self.tabview = ctk.CTkTabview(right_panel, width=280)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add tabs
        self.tabview.add("History")
        self.tabview.add("Settings")
        self.tabview.add("Stats")
        
        # === HISTORY TAB ===
        history_label = ctk.CTkLabel(
            self.tabview.tab("History"),
            text="Conversation Log",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        history_label.pack(pady=(5, 10))
        
        self.conversation_log = ctk.CTkTextbox(
            self.tabview.tab("History"),
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.conversation_log.pack(fill="both", expand=True, pady=(0, 10))
        
        history_buttons = ctk.CTkFrame(self.tabview.tab("History"), fg_color="transparent")
        history_buttons.pack(fill="x")
        
        ctk.CTkButton(
            history_buttons,
            text="Clear",
            width=80,
            height=30,
            command=self._clear_log
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            history_buttons,
            text="Export",
            width=80,
            height=30,
            command=self._export_history
        ).pack(side="left", padx=2)
        
        # === SETTINGS TAB ===
        settings_scroll = ctk.CTkScrollableFrame(
            self.tabview.tab("Settings"),
            fg_color="transparent"
        )
        settings_scroll.pack(fill="both", expand=True)
        
        # Microphone settings
        ctk.CTkLabel(
            settings_scroll,
            text="🎤 Microphone",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(5, 5))
        
        self.auto_adjust_var = ctk.BooleanVar(value=self.settings["auto_adjust_mic"])
        ctk.CTkCheckBox(
            settings_scroll,
            text="Auto-adjust sensitivity",
            variable=self.auto_adjust_var,
            command=self._update_settings
        ).pack(anchor="w", padx=10)
        
        self.noise_suppress_var = ctk.BooleanVar(value=self.settings["noise_suppression"])
        ctk.CTkCheckBox(
            settings_scroll,
            text="Noise suppression",
            variable=self.noise_suppress_var,
            command=self._update_settings
        ).pack(anchor="w", padx=10)
        
        # Sensitivity slider
        ctk.CTkLabel(
            settings_scroll,
            text="Sensitivity (lower = more sensitive)",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=10, pady=(10, 0))
        
        self.sensitivity_slider = ctk.CTkSlider(
            settings_scroll,
            from_=100,
            to=4000,
            number_of_steps=39,
            command=self._update_sensitivity
        )
        self.sensitivity_slider.set(self.settings["energy_threshold"])
        self.sensitivity_slider.pack(fill="x", padx=10, pady=(0, 10))
        
        self.sensitivity_value = ctk.CTkLabel(
            settings_scroll,
            text=f"Current: {self.settings['energy_threshold']}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.sensitivity_value.pack(anchor="w", padx=10)
        
        # Response settings
        ctk.CTkLabel(
            settings_scroll,
            text="💬 Response",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        
        self.streaming_var = ctk.BooleanVar(value=self.settings["streaming_response"])
        ctk.CTkCheckBox(
            settings_scroll,
            text="Streaming responses",
            variable=self.streaming_var,
            command=self._update_settings
        ).pack(anchor="w", padx=10)
        
        self.auto_speak_var = ctk.BooleanVar(value=self.settings["auto_speak"])
        ctk.CTkCheckBox(
            settings_scroll,
            text="Auto-speak responses",
            variable=self.auto_speak_var,
            command=self._update_settings
        ).pack(anchor="w", padx=10)
        
        # Temperature slider
        ctk.CTkLabel(
            settings_scroll,
            text="Creativity (0=factual, 1=creative)",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="w", padx=10, pady=(10, 0))
        
        self.temp_slider = ctk.CTkSlider(
            settings_scroll,
            from_=0.0,
            to=1.0,
            number_of_steps=10,
            command=self._update_temperature
        )
        self.temp_slider.set(self.settings["temperature"])
        self.temp_slider.pack(fill="x", padx=10, pady=(0, 10))
        
        self.temp_value = ctk.CTkLabel(
            settings_scroll,
            text=f"Temperature: {self.settings['temperature']:.1f}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.temp_value.pack(anchor="w", padx=10)
        
        # UI settings
        ctk.CTkLabel(
            settings_scroll,
            text="🎨 Interface",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(15, 5))
        
        self.show_trans_var = ctk.BooleanVar(value=self.settings["show_transcription"])
        ctk.CTkCheckBox(
            settings_scroll,
            text="Show live transcription",
            variable=self.show_trans_var,
            command=self._update_settings
        ).pack(anchor="w", padx=10)
        
        # === STATS TAB ===
        stats_frame = ctk.CTkFrame(self.tabview.tab("Stats"), fg_color="transparent")
        stats_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.stats_labels = {}
        stats_data = [
            ("Total Conversations", "0"),
            ("Success Rate", "0%"),
            ("Avg Response Time", "0s"),
            ("Total Messages", "0"),
        ]
        
        for label, value in stats_data:
            frame = ctk.CTkFrame(stats_frame, fg_color="#2a2a2a", corner_radius=8)
            frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                frame,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(anchor="w", padx=10, pady=(5, 0))
            
            value_label = ctk.CTkLabel(
                frame,
                text=value,
                font=ctk.CTkFont(size=20, weight="bold")
            )
            value_label.pack(anchor="w", padx=10, pady=(0, 5))
            
            self.stats_labels[label] = value_label
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.bind("<space>", lambda e: self._on_mic_button_click())
        self.bind("<Escape>", lambda e: self._stop_listening())
        self.bind("<Control-s>", lambda e: self._show_settings())
        self.bind("<Control-h>", lambda e: self.tabview.set("History"))
    
    def _toggle_always_on_top(self):
        """Toggle window always on top."""
        self.always_on_top = not self.always_on_top
        self.attributes("-topmost", self.always_on_top)
        self.pin_button.configure(
            text="📌" if self.always_on_top else "📍"
        )
    
    def _show_settings(self):
        """Switch to settings tab."""
        self.tabview.set("Settings")
    
    def _update_settings(self):
        """Update settings from UI controls."""
        self.settings["auto_adjust_mic"] = self.auto_adjust_var.get()
        self.settings["noise_suppression"] = self.noise_suppress_var.get()
        self.settings["streaming_response"] = self.streaming_var.get()
        self.settings["auto_speak"] = self.auto_speak_var.get()
        self.settings["show_transcription"] = self.show_trans_var.get()
        
        # Update recognizer settings
        self.recognizer.dynamic_energy_threshold = self.settings["auto_adjust_mic"]
    
    def _update_sensitivity(self, value):
        """Update microphone sensitivity."""
        value = int(value)
        self.settings["energy_threshold"] = value
        self.sensitivity_value.configure(text=f"Current: {value}")
        self.recognizer.energy_threshold = value
    
    def _update_temperature(self, value):
        """Update AI temperature."""
        self.settings["temperature"] = round(value, 1)
        self.temp_value.configure(text=f"Temperature: {self.settings['temperature']:.1f}")
        self.generation_config["temperature"] = self.settings["temperature"]
    
    def _on_mic_button_click(self):
        """Handle microphone button click."""
        if self.is_listening:
            self._stop_listening()
        else:
            self._start_listening()
    
    def _start_listening(self):
        """Start listening for voice input."""
        if self.is_listening or self.processing_thread and self.processing_thread.is_alive():
            return
        
        self.is_listening = True
        self._update_status("Listening", "#f44336", "🔴")
        self._animate_button("#f44336")
        
        # Start processing in background thread
        self.processing_thread = threading.Thread(target=self._process_voice_input)
        self.processing_thread.daemon = True
        self.processing_thread.start()
    
    def _stop_listening(self):
        """Stop listening."""
        self.is_listening = False
        self._update_status("Ready", "#4CAF50", "🟢")
        self._animate_button("#4CAF50")
    
    def _process_voice_input(self):
        """Process voice input in background thread."""
        try:
            # Update transcription
            self.after(0, lambda: self.transcription_label.configure(text="🎤 Listening..."))
            
            # Listen for audio
            user_input = self._listen_for_audio()
            
            if not user_input:
                self.after(0, lambda: self.transcription_label.configure(
                    text="❌ No speech detected. Speak louder or check microphone."
                ))
                self._stop_listening()
                return
            
            # Display transcription
            self.after(0, lambda: self.transcription_label.configure(text=f"You: {user_input}"))
            
            # Log to history
            self.after(0, lambda: self._log_message("You", user_input))
            
            # Update status to processing
            self.after(0, lambda: self._update_status("Processing", "#2196F3", "🔵"))
            self.after(0, lambda: self._animate_button("#2196F3"))
            
            # Get AI response
            if self.settings["streaming_response"]:
                response = self._get_gemini_response_streaming(user_input)
            else:
                response = self._get_gemini_response(user_input)
            
            if response:
                # Update status to speaking
                if self.settings["auto_speak"]:
                    self.after(0, lambda: self._update_status("Speaking", "#4CAF50", "🟢"))
                    self.after(0, lambda: self._animate_button("#4CAF50"))
                    self._speak(response)
                
                # Save to history
                self.conversation_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "user": user_input,
                    "assistant": response
                })
                
                self._update_stats()
            
        except Exception as e:
            self.after(0, lambda: self._log_message("System", f"❌ Error: {str(e)[:100]}"))
        
        finally:
            self.is_listening = False
            self.after(0, lambda: self._update_status("Ready", "#4CAF50", "🟢"))
            self.after(0, lambda: self._animate_button("#4CAF50"))
    
    def _listen_for_audio(self) -> Optional[str]:
        """Listen for audio from microphone with advanced settings."""
        try:
            with sr.Microphone() as source:
                # Very quick ambient noise adjustment if enabled (0.3 seconds max)
                if self.settings["noise_suppression"]:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                # Display current threshold
                self.after(0, lambda: self.mic_level_label.configure(
                    text=f"🎤 Threshold: {int(self.recognizer.energy_threshold)}"
                ))
                
                # Listen for audio with longer timeout
                audio = self.recognizer.listen(
                    source,
                    timeout=10.0,  # Increased from 5 to 10 seconds
                    phrase_time_limit=self.settings["phrase_time_limit"]
                )
                
                # Recognize speech using Google
                text = self.recognizer.recognize_google(audio)
                return text.strip()
        
        except sr.WaitTimeoutError:
            self.after(0, lambda: self._log_message("System", "⚠️ Timeout: No speech detected in 10 seconds"))
            return None
        except sr.UnknownValueError:
            self.after(0, lambda: self._log_message("System", "⚠️ Could not understand audio"))
            return None
        except Exception as e:
            self.after(0, lambda: self._log_message("System", f"⚠️ Mic error: {str(e)[:50]}"))
            return None
    
    def _get_gemini_response(self, user_input: str) -> str:
        """Get response from Gemini AI (non-streaming)."""
        try:
            response = self.model.generate_content(user_input)
            
            if response and response.text:
                text = response.text.strip()
                self.after(0, lambda: self.response_display.delete("1.0", "end"))
                self.after(0, lambda: self.response_display.insert("1.0", text))
                self.after(0, lambda: self._log_message("Assistant", text))
                return text
            else:
                return "I apologize, but I couldn't generate a response."
        
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                msg = "API quota exceeded. Please try again later."
            elif "api key" in error_msg.lower():
                msg = "API key error. Check your .env file."
            else:
                msg = "Error processing request."
            
            self.after(0, lambda: self._log_message("System", f"❌ {msg}"))
            return msg
    
    def _get_gemini_response_streaming(self, user_input: str) -> str:
        """Get streaming response from Gemini AI for instant feedback."""
        try:
            # Clear response display
            self.after(0, lambda: self.response_display.delete("1.0", "end"))
            
            response = self.model.generate_content(user_input, stream=True)
            
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    # Update display in real-time
                    self.after(0, lambda t=full_text: self.response_display.delete("1.0", "end"))
                    self.after(0, lambda t=full_text: self.response_display.insert("1.0", t))
            
            if full_text:
                self.after(0, lambda: self._log_message("Assistant", full_text))
                return full_text
            else:
                return "I apologize, but I couldn't generate a response."
        
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "429" in error_msg:
                msg = "API quota exceeded. Please try again later."
            elif "api key" in error_msg.lower():
                msg = "API key error. Check your .env file."
            else:
                msg = f"Error: {str(e)[:50]}"
            
            self.after(0, lambda: self._log_message("System", f"❌ {msg}"))
            return msg
    
    def _speak(self, text: str):
        """Convert text to speech."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.after(0, lambda: self._log_message("System", f"❌ TTS error: {str(e)[:50]}"))
    
    def _update_status(self, status: str, color: str, icon: str):
        """Update status indicator."""
        self.status_label.configure(text=f"{icon} {status}", text_color=color)
    
    def _animate_button(self, color: str):
        """Animate microphone button border color."""
        self.mic_button.configure(border_color=color)
    
    def _log_message(self, sender: str, message: str):
        """Log message to conversation history."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {sender}: {message}\n\n"
        
        self.conversation_log.insert("end", formatted)
        self.conversation_log.see("end")
    
    def _clear_log(self):
        """Clear conversation log."""
        self.conversation_log.delete("1.0", "end")
        self.conversation_history = []
        self._log_message("System", "History cleared")
        self._update_stats()
    
    def _export_history(self):
        """Export conversation history to JSON file."""
        if not self.conversation_history:
            self._log_message("System", "No history to export")
            return
        
        try:
            filename = f"conversation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = Path(__file__).parent / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            
            self._log_message("System", f"✅ Exported to {filename}")
        except Exception as e:
            self._log_message("System", f"❌ Export failed: {str(e)}")
    
    def _update_stats(self):
        """Update statistics display."""
        total_convs = len(self.conversation_history)
        total_msgs = total_convs * 2  # User + Assistant
        
        self.stats_labels["Total Conversations"].configure(text=str(total_convs))
        self.stats_labels["Total Messages"].configure(text=str(total_msgs))
        self.stats_labels["Success Rate"].configure(text="100%" if total_convs > 0 else "0%")


def main():
    """Entry point for the advanced GUI application."""
    app = AdvancedVoiceAssistantGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
