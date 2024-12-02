from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Game
from chatbot.client import ChatbotClient
import os
import json



@method_decorator(csrf_exempt, name='dispatch')
class ReturnUrlView(View):

    def validate_request_structure(self, data):
        try:
            # Check if all required fields exist
            if not all(key in data for key in ['return_url', 'conversation_id', 'extra_data']):
                return False
            
            # Validate return_url
            if not isinstance(data['return_url'], str):
                return False
            
            # Validate conversation_id
            if not isinstance(data['conversation_id'], str):
                return False
            
            # Validate extra_data
            if not isinstance(data['extra_data'], dict):
                return False
            
            return True
            
        except (KeyError, TypeError, ValueError):
            return False

    def post(self, request, *args, **kwargs):
        # Check Content-Type header
        content_type = request.headers.get('Content-Type', '')
        if 'application/json' not in content_type.lower():
            return HttpResponse(status=415)

        try:
            # Parse JSON data from request body
            data = json.loads(request.body)

            # Validate request structure
            if not self.validate_request_structure(data):
                return HttpResponse(status=400)

            # Extract relevant information
            return_url = data['return_url']
            extra_data = data['extra_data']
            move = int(extra_data.get("position"))
            game_id = int(extra_data.get("game_id"))


            game: Game = Game.objects.get(pk=game_id)
            

            if game.status == 'IN_PROGRESS':
                game.make_move(move)
                if game.status == 'IN_PROGRESS' and not game.bot_move():
                    raise Exception("could not make bot mve")

            # Initialize chatbot client
            client = ChatbotClient(
                api_key=os.environ.get('KENAR_API_KEY'),
            )

            # Get game status message
            status_message = "Your turn! Select a position to play: (you can reset with /restart)"
            if game.status == 'X_WON':
                status_message = "Game Over - You Won! 🎉"
            elif game.status == 'O_WON':
                status_message = "Game Over - Bot Won! 🤖"
            elif game.status == 'DRAW':
                status_message = "Game Over - It's a Draw! 🤝"

            # Get button grid from game and send message
            try:
                client.send_message_with_buttons(
                    conversation_id=game.conversation_id,
                    message=status_message,
                    buttons_data=game.get_button_grid()
                )
            finally:
                client.close()

            return JsonResponse({"url": return_url}, status=200)

        except json.JSONDecodeError:
            return HttpResponse(status=400)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)

