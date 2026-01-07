# LLM-Powered AI Voice Assistant with Function Calling

An advanced, async AI Voice Assistant powered by OpenAI's GPT-4o-mini with function calling capabilities. This is a production-ready agentic system that can have natural conversations and autonomously decide when to use tools.

## 🚀 Features

- **🤖 Agentic Workflow**: Uses OpenAI's function calling (tools API) - the LLM decides when to call functions vs. chat
- **🎤 Advanced STT**: OpenAI Whisper API for high-quality transcription
- **🔊 Neural TTS**: edge-tts with natural-sounding voices
- **⚡ Fully Async**: Built with asyncio for maximum performance
- **🔧 Modular Tools**: Easy to add new capabilities
- **💬 Conversation Memory**: Maintains context across interactions
- **🎯 Production-Ready**: Proper error handling, logging, and architecture

## 📁 Project Structure

```
├── main_async.py        # Async main loop (Whisper + edge-tts + orchestration)
├── agent.py             # VoiceAgent class (LLM + function calling logic)
├── tools.py             # ToolBox class (available functions + schemas)
├── requirements.txt     # Dependencies
├── .env.example         # Environment variables template
└── README_ADVANCED.md   # This file
```

## 🏗️ Architecture

### Three-Layer Design:

1. **main_async.py** (I/O Layer)
   - Captures audio from microphone
   - Transcribes with OpenAI Whisper API
   - Synthesizes responses with edge-tts
   - Fully asynchronous event loop

2. **agent.py** (Brain Layer)
   - `VoiceAgent` class manages conversation
   - Handles OpenAI API calls with tools parameter
   - Implements agentic loop:
     - Send message to LLM
     - If tool call → Execute function → Send result back to LLM
     - If chat → Return response
   - Maintains conversation history

3. **tools.py** (Capability Layer)
   - `ToolBox` class with static methods
   - OpenAI function schemas (TOOL_SCHEMAS)
   - Current tools:
     - `get_current_time()`: Returns time and date
     - `get_current_weather()`: Weather info (dummy data)
     - `search_web()`: Web search (dummy data)
     - `calculate()`: Math operations
     - `get_system_info()`: System details

## 🛠️ Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note on PyAudio:**
- **Windows (Python 3.13+)**: PyAudio should install directly with `pip install PyAudio`. If it fails, use pre-built wheels from [unofficial binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
- **Windows (Python 3.12 and below)**: `pip install pipwin && pipwin install pyaudio` (Note: pipwin doesn't support Python 3.13)
- **Linux**: `sudo apt-get install portaudio19-dev && pip install pyaudio`
- **macOS**: `brew install portaudio && pip install pyaudio`

### 2. Set up OpenAI API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```
OPENAI_API_KEY=sk-your-actual-openai-api-key
```

Or set it directly in your environment:

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key"

# Linux/macOS
export OPENAI_API_KEY="sk-your-key"
```

## 🎮 Usage

### Voice Mode (Full Experience)

```bash
python main_async.py
```

The assistant will:
1. Announce it's ready with voice
2. Listen for your voice commands
3. Process with LLM + function calling
4. Respond with voice

**Try saying:**
- "What time is it?"
- "What's the weather in New York?"
- "Calculate 25 times 17"
- "Tell me about my system"
- "Let's chat about AI"

### Interactive Mode (Text Only)

Perfect for testing without microphone/speakers:

```bash
python main_async.py --interactive
```

## 🔧 How Function Calling Works

### The Agentic Loop

```python
User: "What's the weather in Tokyo?"
  ↓
LLM decides: "I need to call get_current_weather"
  ↓
System executes: get_current_weather(location="Tokyo", unit="celsius")
  ↓
System sends result back to LLM
  ↓
LLM generates natural response: "The weather in Tokyo is currently 22°C and partly cloudy."
  ↓
System speaks the response
```

### When LLM Decides NOT to Use Tools

```python
User: "Tell me a joke"
  ↓
LLM decides: "This is a conversational request, no tool needed"
  ↓
LLM generates response directly
  ↓
System speaks the response
```

## 🎨 Customization

### Adding a New Tool

1. **Add the function to `tools.py`:**

```python
class ToolBox:
    @staticmethod
    def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
        """Send an email."""
        # Implementation here
        return {"status": "success", "message": f"Email sent to {to}"}
```

2. **Add the schema to `TOOL_SCHEMAS` in `tools.py`:**

```python
TOOL_SCHEMAS.append({
    "type": "function",
    "function": {
        "name": "send_email",
        "description": "Send an email to someone",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email content"}
            },
            "required": ["to", "subject", "body"]
        }
    }
})
```

That's it! The LLM will automatically know when to use your new tool.

### Changing the TTS Voice

edge-tts supports many voices. Find available voices:

```bash
edge-tts --list-voices
```

Then modify in `main_async.py`:

```python
assistant = VoiceAssistant(tts_voice="en-GB-RyanNeural")  # British male
assistant = VoiceAssistant(tts_voice="en-US-JennyNeural")  # US female
```

### Customizing the System Prompt

In `agent.py`, modify the `VoiceAgent.__init__` system prompt:

```python
self.system_prompt = (
    "You are JARVIS, Tony Stark's AI assistant. "
    "Be witty, intelligent, and slightly sarcastic. "
    "Use tools when needed and speak concisely."
)
```

## 🔍 Tool Development Guidelines

### Tool Function Rules:

1. Must be a static method in `ToolBox`
2. Must return a `Dict[str, Any]` (JSON-serializable)
3. Should include error handling
4. Should return status indicators

### Good Tool Example:

```python
@staticmethod
def my_tool(param: str) -> Dict[str, Any]:
    """Tool description for the LLM."""
    try:
        result = do_something(param)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

### Tool Schema Rules:

- `name`: Must match the function name exactly
- `description`: Tell the LLM WHEN to use this tool
- `parameters`: JSON Schema format
- `required`: List required parameter names

## 🚨 Troubleshooting

### "No module named 'speech_recognition'"

```bash
pip install -r requirements.txt
```

### "PyAudio not found" / Microphone issues

**For Python 3.13 on Windows:**
1. Try: `pip install PyAudio`
2. If that fails, download the wheel from [Christoph Gohlke's site](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
3. Install with: `pip install path/to/downloaded/PyAudio-x.x.x-cpXXX-cpXXX-win_amd64.whl`

**For older Python versions:**
See installation section for OS-specific PyAudio installation.

### "OpenAI API key not found"

Set the `OPENAI_API_KEY` environment variable or create a `.env` file.

### "TTS not working"

edge-tts requires internet connection. Check your network.

### "playsound error on Windows"

We've replaced `playsound` with `pygame` for better Python 3.13 compatibility.

If you see pygame warnings about `pkg_resources`, they're harmless and can be ignored.

To suppress them, add this at the top of your script:
```python
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

## 📊 API Costs

**OpenAI Usage:**
- **Whisper API**: ~$0.006 per minute of audio
- **GPT-4o-mini**: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens

**Example Session (10 exchanges):**
- Whisper: ~10 seconds × 10 = ~$0.01
- GPT-4o-mini: ~20K tokens = ~$0.015
- **Total**: ~$0.025 per session

**edge-tts**: Free!

## 🎯 Production Considerations

### Security:

- Never commit `.env` with real API keys
- Sanitize tool inputs (especially for system commands)
- The `execute_system_command` tool is intentionally disabled

### Performance:

- Adjust `max_history` in `VoiceAgent` to control context size
- Use streaming for longer responses (see `process_user_input_streaming`)
- Consider caching frequently accessed data

### Reliability:

- All network calls have error handling
- Conversation history is maintained even after errors
- Graceful fallbacks for STT/TTS failures

## 🔮 Future Enhancements

- [ ] Wake word detection ("Hey Assistant!")
- [ ] Real-time streaming (speech while LLM is thinking)
- [ ] Multi-language support
- [ ] Vector database for long-term memory
- [ ] Integration with real APIs (weather, calendar, email)
- [ ] Voice activity detection (VAD) for better listening
- [ ] Custom wake words with Porcupine
- [ ] Web UI dashboard

## 📚 Key Differences from Basic Version

| Feature | Basic Version | Advanced Version |
|---------|--------------|------------------|
| NLU | Keyword matching | GPT-4o-mini with function calling |
| STT | Google Speech | OpenAI Whisper API |
| TTS | pyttsx3 | edge-tts (neural voices) |
| Architecture | Synchronous | Fully async |
| Decision Making | If/else rules | LLM decides autonomously |
| Tool Execution | Direct mapping | Agentic loop with feedback |
| Extensibility | Manual pattern updates | Just add function + schema |

## 📝 License

MIT License - Feel free to use and modify.

## 🤝 Contributing

This is a template project. Feel free to:
- Add new tools
- Improve error handling
- Optimize performance
- Share your enhancements!

## 💡 Tips

1. **Start in interactive mode** to test without hardware
2. **Check logs** for debugging (INFO level by default)
3. **Adjust energy_threshold** in main_async.py for your microphone
4. **Use short, clear commands** for best STT results
5. **Be patient** - Whisper API can take 1-2 seconds

---

**Built with ❤️ using OpenAI, edge-tts, and Python asyncio**
