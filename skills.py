"""
skills.py: Core skills module for the AI Personal Assistant.

Each skill is a function that takes user input and returns a response.
This module is designed to be easily extended with new skills.
"""

from datetime import datetime
from typing import Optional


class SkillNotImplementedError(Exception):
    """Raised when a skill is not yet implemented."""
    pass


def get_time() -> str:
    """
    Returns the current time in HH:MM:SS format.
    
    Returns:
        str: Current time string
    """
    now = datetime.now()
    return f"The current time is {now.strftime('%H:%M:%S')}"


def get_date() -> str:
    """
    Returns the current date in a readable format.
    
    Returns:
        str: Current date string
    """
    now = datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}"


def greet(name: Optional[str] = None) -> str:
    """
    Returns a friendly greeting.
    
    Args:
        name (str, optional): Name of the person to greet.
    
    Returns:
        str: Greeting message
    """
    if name:
        return f"Hello {name}! How can I assist you today?"
    return "Hello! I'm your AI Personal Assistant. How can I help you?"


def get_weather() -> str:
    """
    Returns weather information.
    Currently not implemented - placeholder for future expansion.
    
    Returns:
        str: Weather information or placeholder message
    """
    raise SkillNotImplementedError("Weather skill is not yet implemented.")


def open_app(app_name: str) -> str:
    """
    Simulates opening an application.
    Currently returns a message instead of actually opening apps for safety.
    
    Args:
        app_name (str): Name of the app to open
    
    Returns:
        str: Status message
    """
    return f"I would open {app_name}, but this feature is not yet implemented for safety reasons."


# Skill registry: Maps intent names to skill functions
SKILL_REGISTRY = {
    'time': get_time,
    'date': get_date,
    'greeting': greet,
    'weather': get_weather,
    'open_app': open_app,
}


def execute_skill(intent: str, entities: dict = None) -> str:
    """
    Executes a skill based on the intent.
    
    Args:
        intent (str): The intent name (e.g., 'time', 'greeting')
        entities (dict, optional): Extracted entities from user input
    
    Returns:
        str: Response from the skill
    
    Raises:
        KeyError: If the intent is not recognized
    """
    if entities is None:
        entities = {}
    
    if intent not in SKILL_REGISTRY:
        raise KeyError(f"Unknown intent: {intent}")
    
    skill_func = SKILL_REGISTRY[intent]
    
    # Pass entities as kwargs if available
    try:
        return skill_func(**entities)
    except TypeError:
        # If the skill doesn't accept the entities, call without them
        return skill_func()
