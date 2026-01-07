"""
agent.py: LLM-powered Voice Assistant Agent with OpenAI Function Calling.

This module implements the VoiceAgent class that manages conversation history,
interacts with OpenAI's API, handles function/tool calling, and orchestrates
the agentic workflow.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, AsyncIterator
from openai import AsyncOpenAI
from tools import TOOL_SCHEMAS, get_tool_function


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceAgent:
    """
    LLM-powered conversational agent with function calling capabilities.
    
    Uses OpenAI's GPT-4o-mini with the tools parameter to enable the agent
    to decide when to call functions vs. when to just chat.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        system_prompt: Optional[str] = None,
        max_history: int = 20
    ):
        """
        Initialize the VoiceAgent.
        
        Args:
            api_key (str, optional): OpenAI API key. If None, reads from env.
            model (str): OpenAI model to use
            system_prompt (str, optional): Custom system prompt
            max_history (int): Maximum conversation history to maintain
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.max_history = max_history
        
        # Default system prompt
        self.system_prompt = system_prompt or (
            "You are a helpful, friendly AI voice assistant. "
            "You can have natural conversations and use available tools when needed. "
            "Keep your responses concise and conversational since they will be spoken aloud. "
            "When using tools, explain what you're doing in a natural way. "
            "Today's date is January 7, 2026."
        )
        
        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        logger.info(f"VoiceAgent initialized with model: {self.model}")
    
    def add_message(self, role: str, content: str, name: Optional[str] = None):
        """
        Add a message to conversation history.
        
        Args:
            role (str): Message role ('user', 'assistant', 'tool')
            content (str): Message content
            name (str, optional): Name (for tool responses)
        """
        message = {"role": role, "content": content}
        if name:
            message["name"] = name
        
        self.conversation_history.append(message)
        
        # Trim history if too long (keep system message)
        if len(self.conversation_history) > self.max_history + 1:
            self.conversation_history = [self.conversation_history[0]] + \
                                       self.conversation_history[-(self.max_history):]
    
    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input through the agentic workflow.
        
        This is the core "brain" of the agent:
        1. Add user message to history
        2. Call OpenAI API with tools
        3. If tool call requested: execute tool, add result, call API again
        4. If chat response: return it
        5. Loop until we get a final text response
        
        Args:
            user_input (str): User's message
        
        Returns:
            str: Assistant's response
        """
        logger.info(f"Processing user input: {user_input}")
        
        # Add user message
        self.add_message("user", user_input)
        
        # Agentic loop: Keep calling API until we get a final response
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Agent iteration {iteration}")
            
            try:
                # Call OpenAI API with tools
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=self.conversation_history,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto"  # Let the model decide
                )
                
                assistant_message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason
                
                logger.info(f"Finish reason: {finish_reason}")
                
                # Case 1: Model wants to call tool(s)
                if finish_reason == "tool_calls" and assistant_message.tool_calls:
                    logger.info(f"Model requested {len(assistant_message.tool_calls)} tool call(s)")
                    
                    # Add assistant's tool call message to history
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })
                    
                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"Executing tool: {function_name} with args: {function_args}")
                        
                        # Execute the function
                        try:
                            tool_function = get_tool_function(function_name)
                            function_result = tool_function(**function_args)
                            result_str = json.dumps(function_result)
                            logger.info(f"Tool result: {result_str}")
                        except Exception as e:
                            logger.error(f"Error executing tool {function_name}: {e}")
                            result_str = json.dumps({
                                "status": "error",
                                "error": str(e)
                            })
                        
                        # Add tool result to conversation history
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": result_str
                        })
                    
                    # Continue loop to get assistant's final response
                    continue
                
                # Case 2: Model provided a text response
                elif finish_reason == "stop":
                    final_response = assistant_message.content or "I'm not sure how to respond to that."
                    logger.info(f"Final response: {final_response}")
                    
                    # Add assistant response to history
                    self.add_message("assistant", final_response)
                    
                    return final_response
                
                # Case 3: Other finish reasons (length, content_filter, etc.)
                else:
                    logger.warning(f"Unexpected finish reason: {finish_reason}")
                    fallback = "I apologize, but I encountered an issue processing your request."
                    self.add_message("assistant", fallback)
                    return fallback
            
            except Exception as e:
                logger.error(f"Error in agent processing: {e}")
                error_response = "I'm sorry, I encountered an error while processing your request."
                self.add_message("assistant", error_response)
                return error_response
        
        # Max iterations reached
        logger.warning(f"Max iterations ({max_iterations}) reached")
        timeout_response = "I apologize, but I'm having trouble completing that request."
        self.add_message("assistant", timeout_response)
        return timeout_response
    
    async def process_user_input_streaming(self, user_input: str) -> AsyncIterator[str]:
        """
        Process user input with streaming response.
        Note: Streaming doesn't work well with tool calls, so this is for chat-only mode.
        
        Args:
            user_input (str): User's message
        
        Yields:
            str: Chunks of assistant's response
        """
        logger.info(f"Processing user input (streaming): {user_input}")
        
        # Add user message
        self.add_message("user", user_input)
        
        try:
            # Call OpenAI API with streaming
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                stream=True
            )
            
            full_response = ""
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield content
            
            # Add complete response to history
            self.add_message("assistant", full_response)
        
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield "I'm sorry, I encountered an error."
    
    def reset_conversation(self):
        """Reset conversation history, keeping only the system prompt."""
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        logger.info("Conversation history reset")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history."""
        return self.conversation_history
    
    def set_system_prompt(self, prompt: str):
        """
        Update the system prompt.
        
        Args:
            prompt (str): New system prompt
        """
        self.system_prompt = prompt
        self.conversation_history[0] = {"role": "system", "content": prompt}
        logger.info("System prompt updated")
