from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from xo.models import Game
from .models import ConversationQuota
from .client import ChatbotClient, ClaudeClient
import json
import os

@method_decorator(csrf_exempt, name='dispatch')
class MessageWebhookView(View):
    def validate_message_structure(self, data):
        try:

            new_message = data.get('new_chatbot_message', {})
            if not isinstance(new_message, dict):
                return False

            # Check new_message structure
            if not all([
                isinstance(new_message.get('id'), str),
                isinstance(new_message.get('type'), str),
                isinstance(new_message.get('text'), str),
            ]):
                return False

            # Check conversation structure
            conversation = new_message.get('conversation', {})
            if not all([
                isinstance(conversation.get('id'), str),
            ]):
                return False


            return True

        except (KeyError, TypeError, ValueError):
            return False

    def post(self, request, *args, **kwargs):
        # Check Content-Type header
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type.lower():
            return HttpResponse(
                status=415
            )

        try:
            # Parse JSON data from request body
            data = json.loads(request.body)

            # Validate message structure
            if not self.validate_message_structure(data):
                return JsonResponse(
                    {'error': 'Invalid message structure'},
                    status=400
                )

            # Extract relevant information
            conversation_id = data['new_chatbot_message']['conversation']['id']
            text = data['new_chatbot_message']['text']

            client = ChatbotClient(
                api_key=os.environ.get('KENAR_API_KEY'),
            )
            
            # Handle restart command
            if text.strip().lower().startswith('/hajehsan'):
                conversation_quota = ConversationQuota.objects.get_or_create(conversation_id=conversation_id)
                if conversation_quota.get_remaining_quota() == 0:
                    return HttpResponse(b"", status=429)
                conversation_quota.increment_quota()
                ai_client = ClaudeClient(api_key=os.environ.get("ANTROPIC_API_KEY"), base_url=os.environ.get("ANTROPIC_BASE_URL", None))
                response = ai_client.get_response(text.strip()[len("/hajehsan"):])
                client.send_message_with_buttons(conversation_id, response, None)
                return HttpResponse(status=200)

            elif text.strip().lower().startswith('/restart'):
                # Delete existing game if it exists
                Game.objects.filter(conversation_id=conversation_id).delete()
                # Create new game
                game = Game.objects.create(
                    conversation_id=conversation_id,
                )
            else:
                # Get or create game normally
                game, created = Game.objects.get_or_create(
                    conversation_id=conversation_id,
                )


            # Initialize chatbot client

            # Get game status message
            status_message = "Your turn! Select a position to play: (you can reset with /restart)"
            if game.status == 'X_WON':
                status_message = "Game Over - You Won! 🎉\nUse /restart to rest"
            elif game.status == 'O_WON':
                status_message = "Game Over - Bot Won! 🤖"
            elif game.status == 'DRAW':
                status_message = "Game Over - It's a Draw! 🤝"

            game_button_grid = game.get_button_grid()

            # Get button grid from game and send message
            try:
                client.send_message_with_buttons(
                    conversation_id=conversation_id,
                    message=status_message,
                    buttons_data=game_button_grid
                )
            finally:
                client.close()


            return HttpResponse(status=200)

        except json.JSONDecodeError:
            print("dsaads")
            return HttpResponse(status=400)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

