import httpx
from typing import Dict, List, Optional, Union
import json
import os
from anthropic import Anthropic

class ChatbotClient:
    def __init__(self, api_key: str):
        self.base_url = "https://api.divar.ir" 
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': api_key,
        }
        self.client = httpx.Client(timeout=30.0)

    def create_button(self, caption: str, icon_name: str, action_data: Dict) -> Dict:
        """Create a button structure"""
        return {
            "action": {
                "open_server_link": {
                    "data": action_data
                }
            },
            "icon_name": icon_name,
            "caption": caption
        }

    def send_message_with_buttons(
        self,
        conversation_id: str,
        message: str,
        buttons_data: Optional[List[Dict[str, str]]],
        message_type: str = "TEXT"
    ) -> httpx.Response:
        """
        Send a message with buttons
        
        Args:
            message: The text message to send
            buttons_data: List of dictionaries containing button data
                        [{"caption": "Button Text", "icon_name": "icon", "data": {...}}] message_type: Type of message (default: "TEXT")
        """
        # Create buttons

        # Construct the payload
        payload = {
            "type": message_type,
            "text_message": message,
            "buttons": {
                 "rows": buttons_data 
            }
        }

        print(payload)
        try:
            response = self.client.post( 
                f"{self.base_url}/experimental/open-platform/chatbot-conversations/{conversation_id}/messages",  # Adjust endpoint as needed
                headers=self.headers,
                json=payload
            )
            print(response.json())
            response.raise_for_status()
            return response
        except httpx.HTTPError as e:
            raise Exception(f"Failed to send message: {str(e)}")

    def close(self):
        """Close the HTTP client"""
        self.client.close()


class ClaudeClient:
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize Claude client with API key and optional base URL
        
        Args:
            api_key: Anthropic API key
            base_url: Optional base URL for API endpoint (default: None, uses Anthropic's default)
        """
        self.client = Anthropic(
            api_key=api_key,
            base_url=base_url if base_url else "https://api.anthropic.com"
        )
        self.model = "claude-3-sonnet-20241022"

    def get_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Get a response from Claude API
        
        Args:
            prompt: The user's message/prompt
            system_prompt: Optional system prompt to set context/behavior
            max_tokens: Maximum tokens in response (default: 1000)
            temperature: Response randomness (0-1, default: 0.7)
            
        Returns:
            str: Claude's response text
        """
        try:
            messages = []
            
            # Add system prompt if provided
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add user message
            messages.append({
                "role": "user",
                "content": prompt
            })

            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            raise Exception(f"Failed to get Claude response: {str(e)}")

    def close(self):
        """Clean up resources if needed"""
        pass  # Anthropic client doesn't need explicit cleanup
