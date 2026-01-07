# Quick Start Guide - AI Voice Assistant

## ✅ Installation Status

**All dependencies installed!** ✅
- OpenAI SDK ✅
- edge-tts ✅  
- SpeechRecognition ✅
- PyAudio ✅
- Pygame ✅

**Microphones detected:** ✅ (9 input devices found)

## 🧪 Test Without API Key (Recommended First!)

Before setting up OpenAI, test that everything works:

```powershell
python demo_offline.py
```

This will test:
- ✅ Microphone recording
- ✅ Text-to-speech (you'll hear it!)
- ✅ Tool execution
- ✅ Full workflow simulation

## 🔑 Set Your OpenAI API Key

Get your API key from: https://platform.openai.com/api-keys

**Method 1: PowerShell (Temporary)**
```powershell
$env:OPENAI_API_KEY="sk-your-actual-api-key-here"
```

**Method 2: Create `.env` file (Persistent)**
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Verify it's set:**
```powershell
python test_setup.py
```

### 2. Test in Interactive Mode (Recommended First)

This mode uses text input/output - no microphone or speakers needed:

```powershell
python main_async.py --interactive
```

**What to expect:**
- Type your commands (no voice)
- LLM processes with function calling
- Responses are spoken AND printed

Try these commands:
- "What time is it?"
- "Calculate 25 times 47"
- "Tell me a joke"
- "What's the weather in London?"
- "Tell me about my system"

Type `exit` to quit.

### 3. Run with Voice I/O (Full Experience)

Once you confirm it works in interactive mode:

```powershell
python main_async.py
```

The assistant will:
- 🔊 Speak a welcome message
- 🎤 Listen for your voice commands
- 🧠 Process with GPT-4o-mini + function calling
- 🔊 Respond with a natural voice

Say `goodbye` or `exit` to quit.

## 🎨 Example Conversations

**Time & Date:**
- "What time is it?"
- "What's today's date?"

**Math:**
- "Calculate 123 times 456"
- "What's the square root of 144?"

**System Info:**
- "What system am I running?"
- "Tell me about my computer"

**Weather (dummy data):**
- "What's the weather in Tokyo?"
- "How's the weather in Paris?"

**Web Search (dummy data):**
- "Search for Python tutorials"

**General Chat:**
- "Tell me a joke"
- "What do you think about AI?"
- "Let's have a conversation"

## 🛠️ Customization

### Change the Voice

Available voices (preview at: https://tts.travisvn.com/):
- `en-US-AriaNeural` (Female, friendly)
- `en-US-GuyNeural` (Male, professional)
- `en-US-JennyNeural` (Female, warm)
- `en-GB-SoniaNeural` (British female)
- `en-GB-RyanNeural` (British male)

Edit `main_async.py`:
```python
assistant = VoiceAssistant(tts_voice="en-GB-RyanNeural")
```

### Add Your Own Tools

See [README_ADVANCED.md](README_ADVANCED.md) for detailed instructions on adding custom tools.

## 🚨 Troubleshooting

### "OpenAI API key not found"
Set the `OPENAI_API_KEY` environment variable (see step 1 above).

### "Microphone not working"
1. Check your microphone is connected
2. Ensure PyAudio is installed: `pip list | Select-String PyAudio`
3. Try interactive mode first: `python main_async.py --interactive`

### "No module named 'openai'"
Run: `pip install -r requirements.txt`

### Import errors
Make sure you're in the correct directory:
```powershell
cd "C:\Users\adity\OneDrive\Desktop\Aditya\AI Personal Assistant"
```

## 📊 Cost Estimate

- **Whisper API**: ~$0.006 per minute of audio
- **GPT-4o-mini**: ~$0.15/$0.60 per 1M tokens (input/output)
- **edge-tts**: Free!

A typical 10-minute conversation: ~$0.10

## 📚 Documentation

- [README_ADVANCED.md](README_ADVANCED.md) - Complete documentation
- [tools.py](tools.py) - Available tools and how to add more
- [agent.py](agent.py) - How the agentic workflow works

## 🎉 You're Ready!

Start with interactive mode to test everything:
```powershell
python main_async.py --interactive
```

Enjoy your AI assistant! 🤖
