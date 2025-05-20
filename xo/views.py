from django.views import View
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Game
from chatbot.client import ChatbotClient
import os
import json


@method_decorator(csrf_exempt, name="dispatch")
class ReturnUrlView(View):

    def post(self, request, *args, **kwargs):
        # Check Content-Type headerFailed to send message: Server error '500 Internal Server Error' for url 'https://open-api.divar.ir/experimental/open-platform/chat/bot/conversations/92c094e9-c6ec-403f-85bf-4cbae16284e5/messages'
        content_type = request.headers.get("Content-Type", "")
        if "application/json" not in content_type.lower():
            return HttpResponse(status=415)

        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            print(data)

            # Extract relevant information
            extra_data = data["extra_data"]
            move = int(extra_data.get("position"))
            game_id = int(extra_data.get("game_id"))

            game: Game = Game.objects.get(pk=game_id)

            if game.status == "IN_PROGRESS":
                game.make_move(move)
                if game.status == "IN_PROGRESS" and not game.bot_move():
                    return JsonResponse(
                        {"text_message": "you can not make this move"}, status=200
                    )

            # Initialize chatbot client
            client = ChatbotClient(
                api_key=os.environ.get("KENAR_API_KEY"),
            )

            # Get game status message
            status_message = (
                "Your turn! Select a position to play: (you can reset with /restart)"
            )
            if game.status == "X_WON":
                status_message = "Game Over - You Won! 🎉"
            elif game.status == "O_WON":
                status_message = "Game Over - Bot Won! 🤖"
            elif game.status == "DRAW":
                status_message = "Game Over - It's a Draw! 🤝"

            # Get button grid from game and send message
            try:
                client.send_message_with_buttons(
                    conversation_id=game.conversation_id,
                    message=status_message,
                    buttons_data=game.get_button_grid(),
                )
            finally:
                client.close()

            return JsonResponse({"text_message": status_message}, status=200)

        except json.JSONDecodeError:
            return HttpResponse(status=400)
        except Exception as e:
            print(e)
            return HttpResponse(status=500)
