"""
tools.py: ToolBox for the LLM-powered Voice Assistant Agent.

Contains all callable tools/functions that the LLM can invoke.
Each tool must have a corresponding OpenAI function schema.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import platform
import os


class ToolBox:
    """
    Static methods that the LLM can call through OpenAI's function calling.
    Each method here should have a corresponding schema in TOOL_SCHEMAS.
    """
    
    @staticmethod
    def get_current_time(timezone: str = "local") -> Dict[str, Any]:
        """
        Get the current time.
        
        Args:
            timezone (str): The timezone (currently only 'local' is supported)
        
        Returns:
            dict: Current time information
        """
        now = datetime.now()
        return {
            "status": "success",
            "time": now.strftime("%H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "day_of_week": now.strftime("%A"),
            "timezone": timezone
        }
    
    @staticmethod
    def get_current_weather(location: str, unit: str = "celsius") -> Dict[str, Any]:
        """
        Get the current weather for a location.
        (This is a dummy implementation - integrate a real weather API in production)
        
        Args:
            location (str): City name or location
            unit (str): Temperature unit ('celsius' or 'fahrenheit')
        
        Returns:
            dict: Weather information
        """
        # Dummy data - in production, call a weather API (OpenWeatherMap, WeatherAPI, etc.)
        dummy_weather = {
            "status": "success",
            "location": location,
            "temperature": 22 if unit == "celsius" else 72,
            "unit": unit,
            "condition": "Partly Cloudy",
            "humidity": 65,
            "wind_speed": 15,
            "note": "This is dummy data. Integrate a real weather API for production use."
        }
        return dummy_weather
    
    @staticmethod
    def search_web(query: str, num_results: int = 3) -> Dict[str, Any]:
        """
        Search the web for information.
        (This is a dummy implementation - integrate a real search API in production)
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
        
        Returns:
            dict: Search results
        """
        # Dummy data - in production, use Google Custom Search, DuckDuckGo API, etc.
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "title": f"Result {i+1} for '{query}'",
                    "snippet": f"This is a dummy search result snippet for {query}",
                    "url": f"https://example.com/result{i+1}"
                }
                for i in range(min(num_results, 3))
            ],
            "note": "This is dummy data. Integrate a real search API for production use."
        }
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """
        Get system information about the computer.
        
        Returns:
            dict: System information
        """
        return {
            "status": "success",
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version()
        }
    
    @staticmethod
    def execute_system_command(command: str) -> Dict[str, Any]:
        """
        Execute a system command (USE WITH CAUTION).
        This is disabled by default for security reasons.
        
        Args:
            command (str): System command to execute
        
        Returns:
            dict: Command execution result
        """
        # SECURITY: This is intentionally disabled for safety
        return {
            "status": "error",
            "message": "System command execution is disabled for security reasons.",
            "command": command,
            "note": "To enable this, modify the execute_system_command function and implement proper security controls."
        }
    
    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        """
        Perform mathematical calculations.
        
        Args:
            expression (str): Mathematical expression to evaluate
        
        Returns:
            dict: Calculation result
        """
        try:
            # Use eval with safety constraints
            # Only allow numbers, operators, and basic math functions
            allowed_names = {
                "abs": abs, "round": round, "min": min, "max": max,
                "sum": sum, "pow": pow
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return {
                "status": "success",
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "expression": expression,
                "error": str(e)
            }


# OpenAI Function Schemas
# These schemas tell the LLM what functions are available and how to call them
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time and date. Use this when the user asks about the time or date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "enum": ["local"],
                        "description": "The timezone (currently only 'local' is supported)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a specific location. Use this when the user asks about weather conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city or location name, e.g., 'New York', 'London', 'Tokyo'"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit"
                    }
                },
                "required": ["location"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information. Use this when the user asks you to look up information you don't know.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of search results to return (1-5)",
                        "minimum": 1,
                        "maximum": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get information about the computer system. Use this when the user asks about system specifications or OS details.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculations. Use this when the user asks to calculate or solve math problems.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression to evaluate, e.g., '2 + 2', '10 * 5', 'pow(2, 8)'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


def get_tool_function(function_name: str):
    """
    Get a tool function by name.
    
    Args:
        function_name (str): Name of the function to retrieve
    
    Returns:
        callable: The function from ToolBox
    
    Raises:
        AttributeError: If function doesn't exist
    """
    return getattr(ToolBox, function_name)
