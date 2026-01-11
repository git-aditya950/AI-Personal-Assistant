# AI Personal Assistant

A modular, scalable AI Personal Assistant built with Python. Designed for clean architecture with easy extensibility.

## Project Structure

```
├── main.py              # Main orchestration and speech I/O loop
├── skills.py            # Skill implementations (Time, Date, Greeting, etc.)
├── nlu_engine.py        # Natural Language Understanding engine
├── requirements.txt     # Python dependencies
└── README.md            # This file
``` 

## Architecture

The project follows a clean, modular architecture:

1. **main.py**: Orchestrates the core cycle
   - `Listen`: Captures audio from microphone using `speech_recognition`
   - `Understand`: Sends text to NLU engine
   - `Act`: Executes the appropriate skill
   - `Respond`: Converts response to speech using `pyttsx3`

2. **nlu_engine.py**: Natural Language Understanding
   - Currently uses keyword-based intent matching
   - Easily swappable for ML models (spaCy, transformers, etc.)
   - Extracts entities from user input
   - Returns `Intent` objects with confidence scores

3. **skills.py**: Core functionality
   - Modular skill implementation
   - Registry pattern for skill management
   - Easy to add new skills
   - Current skills: Time, Date, Greeting

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Speech Recognition Mode (Default)
```bash
python main.py
```
Starts the assistant with microphone input. The assistant will:
- Announce it's ready
- Listen for voice commands
- Respond with speech

**Commands:**
- "What time is it?" → Returns current time
- "What's the date?" → Returns today's date
- "Hello!" or "Hi!" → Returns a greeting
- "Exit" or "Quit" → Shuts down the assistant

### Interactive Mode (Text Input)
```bash
python main.py --interactive
```
Useful for testing without a microphone or in noisy environments.

## Extending the Assistant

### Adding a New Skill

1. **Add the skill function in `skills.py`:**
   ```python
   def my_skill(param1: str = None) -> str:
       """Docstring explaining the skill."""
       return "Response to the user"
   ```

2. **Register it in the `SKILL_REGISTRY`:**
   ```python
   SKILL_REGISTRY = {
       # ... existing skills ...
       'my_intent': my_skill,
   }
   ```

3. **Add patterns to `nlu_engine.py`:**
   ```python
   INTENT_PATTERNS = {
       # ... existing intents ...
       'my_intent': {
           'keywords': ['keyword1', 'keyword2'],
           'patterns': [r'regex_pattern_1', r'regex_pattern_2'],
       },
   }
   ```

### Upgrading the NLU Engine

To replace keyword-based matching with ML:

1. Keep the `understand(user_input)` function signature in `nlu_engine.py`
2. Replace `extract_intent_keyword_based()` with your ML implementation
3. No changes needed in `main.py` or `skills.py`

Example with spaCy:
```python
def understand(user_input: str) -> Intent:
    # Load your spaCy model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(user_input)
    
    # Your ML-based intent extraction logic here
    # Return Intent object as before
    return Intent(name=intent_name, confidence=score, entities=entities_dict)
```

## Error Handling

The assistant gracefully handles:
- **Microphone timeout**: Prompts user to repeat
- **Speech recognition errors**: Informs user and continues listening
- **Unknown intents**: Suggests alternative commands
- **Unimplemented skills**: Informs user the feature is not available
- **Exceptions**: Logs errors and continues operation

## Logging

All activities are logged to console with timestamps. Check the logs for debugging:
- INFO: Normal operation
- WARNING: Non-critical issues (e.g., timeouts)
- ERROR: Critical errors

## Requirements

- Python 3.10+
- `speech-recognition`: For microphone input
- `pyttsx3`: For text-to-speech output

## Future Enhancements

- [ ] ML-based intent recognition (spaCy, transformers)
- [ ] Database for storing user preferences
- [ ] Weather API integration
- [ ] Calendar integration
- [ ] Custom command execution
- [ ] Multi-language support
- [ ] Wake-word detection ("Hey Assistant!")
- [ ] Persistent skill learning

## License

MIT License - Feel free to use and modify this project.
