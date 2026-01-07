# 🎨 Modern GUI Voice Assistant

A beautiful, modern GUI-based AI Voice Assistant with real-time visual feedback.

## ✨ Features

- 🎨 **Modern Dark Theme** using CustomTkinter
- 🎤 **Large Circular Microphone Button** with visual feedback
- 🚦 **Real-Time Status Indicators**:
  - 🔴 RED: Listening to your voice
  - 🔵 BLUE: Processing with Gemini AI
  - 🟢 GREEN: Speaking the response
- 📝 **Scrolling Conversation Log** to track your chat
- 🔝 **Always-On-Top Window** floats over other apps
- 🧵 **Threaded Processing** - GUI never freezes
- 🎯 **High Accuracy** - Gemini configured with temperature 0.3

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install customtkinter
pip install google-genai
pip install pyttsx3
```

(PyAudio and SpeechRecognition should already be installed)

Or install all at once:
```powershell
pip install -r requirements_gui.txt
```

### 2. Get Gemini API Key

Get your FREE Gemini API key from: https://aistudio.google.com/app/apikey

### 3. Set Your API Key

**Method 1: PowerShell (Temporary)**
```powershell
$env:GEMINI_API_KEY="AIzaSyCSK2suP0DzwcQ7sGZKYW3JwG7XQomawP8"
```

**Method 2: .env File (Persistent)**
```
GEMINI_API_KEY=AIzaSyCSK2suP0DzwcQ7sGZKYW3JwG7XQomawP8
```

### 4. Run the GUI

```powershell
python main_gui.py
```

## 🎮 How to Use

1. **Launch** the application - a modern dark window appears
2. **Click** the large microphone button 🎤
3. **Watch** the border turn RED - start speaking
4. **See** it turn BLUE - AI is processing your request
5. **Observe** it turn GREEN - AI is speaking the response
6. **Read** the conversation log at the bottom
7. **Repeat** - click the mic button again for another query

Say "goodbye" or "exit" to close the application.

## 🎨 Visual Feedback Guide

| Border Color | Status | What's Happening |
|-------------|---------|------------------|
| 🔴 **Red** | Listening | Microphone is active, speak now |
| 🔵 **Blue** | Processing | Gemini AI is analyzing your query |
| 🟢 **Green** | Speaking | TTS engine is responding |
| ⚪ **Gray** | Ready | Click mic button to start |

## 🧠 AI Configuration

The Gemini model is configured for maximum accuracy:

- **Model**: Gemini 1.5 Flash (fast and accurate)
- **Temperature**: 0.3 (low = more deterministic)
- **System Instruction**: Analyzes queries for ambiguity and provides verified answers
- **Safety**: Configured to avoid guessing - acknowledges uncertainty

## 📋 Sample Commands

Try asking:
- "What's the capital of France?"
- "Calculate 25 times 37"
- "Tell me a fun fact about space"
- "What's the weather like today?" (if you have weather integration)
- "Set a reminder for tomorrow"

## 🔧 Customization

### Change Window Size

Edit in `main_gui.py`:
```python
self.geometry("500x700")  # width x height
```

### Change TTS Voice Speed

Edit in `main_gui.py`:
```python
self.tts_engine.setProperty('rate', 150)  # Increase for faster
```

### Change Button Size

Edit in `main_gui.py`:
```python
width=200,
height=200,
corner_radius=100,  # Half of width/height for perfect circle
```

### Change Theme

Edit in `main_gui.py`:
```python
ctk.set_appearance_mode("dark")  # or "light" or "system"
ctk.set_default_color_theme("blue")  # or "green" or "dark-blue"
```

## 🆚 Comparison: GUI vs CLI Versions

| Feature | main_gui.py | main_async.py |
|---------|-------------|---------------|
| Interface | Modern GUI | Command Line |
| AI Model | Gemini (Google) | GPT-4o-mini (OpenAI) |
| Visual Feedback | Color-coded button | Text only |
| Threading | Yes (responsive) | Async (concurrent) |
| TTS | pyttsx3 (local) | edge-tts (cloud) |
| STT | Google (free) | Whisper API (paid) |
| Function Calling | No | Yes |
| Cost | FREE (Gemini free tier) | ~$0.10 per session |
| Best For | Desktop use, visual | Automation, scripting |

## ❓ Troubleshooting

### "GEMINI_API_KEY not found"
Set the environment variable or create a `.env` file.

### "customtkinter not found"
```powershell
pip install customtkinter
```

### Window doesn't stay on top
Some window managers override this. Try running as administrator.

### Microphone not working
Check that PyAudio is installed and your microphone is connected:
```powershell
python test_setup.py
```

### TTS not working
Make sure pyttsx3 is installed:
```powershell
pip install pyttsx3
```

## 🎉 Enjoy!

Your modern GUI voice assistant is ready to use! Click the microphone and start chatting.

---

**Note:** This GUI version uses Gemini API (free tier available) instead of OpenAI. If you prefer OpenAI with function calling, use `main_async.py` instead.
