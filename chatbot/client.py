import httpx
from typing import Dict, List, Optional
import json

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
        buttons_data: List[Dict[str, str]],
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
                f"{self.base_url}/v2/open-platform/chatbot-conversations/{conversation_id}/messages",  # Adjust endpoint as needed
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
