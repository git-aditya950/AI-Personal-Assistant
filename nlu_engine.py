"""
nlu_engine.py: Natural Language Understanding engine for the AI Personal Assistant.

This module handles intent recognition and entity extraction.
Currently uses keyword-based matching for simplicity.
Can be easily extended to use ML models (spaCy, BERT, etc.) later.
"""

from typing import Tuple, Dict, List
import re


class Intent:
    """
    Represents an intent extracted from user input.
    """
    def __init__(self, name: str, confidence: float = 1.0, entities: Dict = None):
        """
        Initialize an Intent.
        
        Args:
            name (str): Intent name (e.g., 'time', 'greeting')
            confidence (float): Confidence score (0.0 to 1.0)
            entities (dict, optional): Extracted entities
        """
        self.name = name
        self.confidence = confidence
        self.entities = entities or {}
    
    def __repr__(self):
        return f"Intent(name='{self.name}', confidence={self.confidence}, entities={self.entities})"


# Intent patterns: Maps keywords/phrases to intents
INTENT_PATTERNS = {
    'time': {
        'keywords': ['time', 'what time', 'current time', 'tell me time', 'what\'s the time'],
        'patterns': [r'(?:what\s+)?time.*', r'.*time.*'],
    },
    'date': {
        'keywords': ['date', 'what date', 'today', 'day', 'what day'],
        'patterns': [r'(?:what\s+)?date.*', r'(?:what\s+)?day.*', r'.*today.*'],
    },
    'greeting': {
        'keywords': ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'],
        'patterns': [r'^(?:hello|hi|hey|greetings).*', r'.*good\s+(?:morning|afternoon|evening).*'],
    },
    'weather': {
        'keywords': ['weather', 'temperature', 'rain', 'sunny', 'forecast'],
        'patterns': [r'.*weather.*', r'.*temperature.*', r'.*rain.*', r'.*forecast.*'],
    },
    'open_app': {
        'keywords': ['open', 'launch', 'start'],
        'patterns': [r'(?:open|launch|start)\s+(\w+)', r'(?:open|launch|start)\s+(\w+\s+\w+)'],
    },
}


def tokenize(text: str) -> List[str]:
    """
    Simple tokenization: converts text to lowercase and splits on whitespace.
    
    Args:
        text (str): Input text
    
    Returns:
        list: List of tokens
    """
    return text.lower().strip().split()


def extract_intent_keyword_based(user_input: str) -> Intent:
    """
    Extract intent using keyword matching.
    This is a simple approach suitable for the initial phase.
    
    Args:
        user_input (str): Raw user input
    
    Returns:
        Intent: Extracted intent object
    """
    user_input_lower = user_input.lower()
    max_matches = 0
    detected_intent = None
    
    # Check each intent's patterns
    for intent_name, intent_data in INTENT_PATTERNS.items():
        # Check keywords
        keyword_matches = sum(1 for kw in intent_data['keywords'] if kw in user_input_lower)
        
        # Check regex patterns
        pattern_matches = sum(1 for pattern in intent_data['patterns'] if re.match(pattern, user_input_lower))
        
        total_matches = keyword_matches + pattern_matches
        
        if total_matches > max_matches:
            max_matches = total_matches
            detected_intent = intent_name
    
    # Default to greeting if no matches
    if detected_intent is None:
        detected_intent = 'greeting'
        confidence = 0.3
    else:
        confidence = min(1.0, max_matches / 2.0)
    
    # Extract entities (e.g., app names from "open spotify")
    entities = extract_entities(user_input, detected_intent)
    
    return Intent(name=detected_intent, confidence=confidence, entities=entities)


def extract_entities(user_input: str, intent: str) -> Dict:
    """
    Extract entities from user input based on the detected intent.
    
    Args:
        user_input (str): Raw user input
        intent (str): Detected intent name
    
    Returns:
        dict: Dictionary of extracted entities
    """
    entities = {}
    
    if intent == 'open_app':
        # Extract app name from patterns like "open spotify"
        match = re.search(r'(?:open|launch|start)\s+([a-z]+(?:\s+[a-z]+)?)', user_input.lower())
        if match:
            entities['app_name'] = match.group(1).strip()
    
    elif intent == 'greeting':
        # Try to extract a name if present
        name_patterns = [
            r"(?:hello|hi|hey)\s+(\w+)",
            r"i'm\s+(\w+)",
            r"my\s+name\s+is\s+(\w+)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, user_input.lower())
            if match:
                entities['name'] = match.group(1).capitalize()
                break
    
    return entities


def understand(user_input: str) -> Intent:
    """
    Main entry point for NLU.
    Processes user input and returns an Intent object.
    
    Args:
        user_input (str): Raw user input text
    
    Returns:
        Intent: Intent object with name, confidence, and entities
    """
    if not user_input or not user_input.strip():
        return Intent(name='greeting', confidence=0.0, entities={})
    
    return extract_intent_keyword_based(user_input)
