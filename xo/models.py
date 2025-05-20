from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Game(models.Model):
    GAME_STATUS_CHOICES = [
        ("IN_PROGRESS", "In Progress"),
        ("X_WON", "X Won"),
        ("O_WON", "O Won"),
        ("DRAW", "Draw"),
    ]

    conversation_id = models.CharField(max_length=100, unique=True)
    board = models.CharField(
        max_length=9, default="---------"
    )  # - for empty, X for player, O for bot
    current_turn = models.CharField(max_length=1, default="X")  # X or O
    status = models.CharField(
        max_length=20, choices=GAME_STATUS_CHOICES, default="IN_PROGRESS"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.conversation_id} - {self.status}"

    def make_move(self, position):
        if not (0 <= position <= 8):
            raise ValueError("Position must be between 0 and 8")

        if self.board[position] != "-":
            raise ValueError("Position already taken")

        board_list = list(self.board)
        board_list[position] = self.current_turn
        self.board = "".join(board_list)

        # Check game status before changing turn
        if self.is_winner(self.current_turn):
            self.status = f"{self.current_turn}_WON"
        elif "-" not in self.board:
            self.status = "DRAW"
        else:
            self.current_turn = "O" if self.current_turn == "X" else "X"

        self.save()

    def get_board_state(self):
        return [list(self.board[i : i + 3]) for i in range(0, 9, 3)]

    def is_winner(self, player):
        # Check rows
        for i in range(0, 9, 3):
            if self.board[i : i + 3] == player * 3:
                return True

        # Check columns
        for i in range(3):
            if self.board[i] == self.board[i + 3] == self.board[i + 6] == player:
                return True

        # Check diagonals
        if self.board[0] == self.board[4] == self.board[8] == player:
            return True
        if self.board[2] == self.board[4] == self.board[6] == player:
            return True

        return False

    def check_game_status(self):
        if self.is_winner("X"):
            self.status = "X_WON"
        elif self.is_winner("O"):
            self.status = "O_WON"
        elif "-" not in self.board:
            self.status = "DRAW"
        self.save()

    def get_winning_move(self, player):
        # Check if there's a winning move for the given player
        for i in range(9):
            if self.board[i] == "-":
                # Try the move
                board_list = list(self.board)
                board_list[i] = player
                temp_board = "".join(board_list)

                # Check rows
                for j in range(0, 9, 3):
                    if temp_board[j : j + 3] == player * 3:
                        return i

                # Check columns
                for j in range(3):
                    if (
                        temp_board[j]
                        == temp_board[j + 3]
                        == temp_board[j + 6]
                        == player
                    ):
                        return i

                # Check diagonals
                if temp_board[0] == temp_board[4] == temp_board[8] == player:
                    return i
                if temp_board[2] == temp_board[4] == temp_board[6] == player:
                    return i

        return None

    def get_strategic_move(self):
        # Priority positions (center, corners, then sides)
        priority_positions = [4, 0, 2, 6, 8, 1, 3, 5, 7]

        for pos in priority_positions:
            if self.board[pos] == "-":
                return pos
        return None

    def bot_move(self):
        """
        Bot (O) makes a move using the following strategy:
        1. Win if possible
        2. Block player's winning move
        3. Make a strategic move
        """
        if self.current_turn != "O" or self.status != "IN_PROGRESS":
            return False

        # Try to win
        winning_move = self.get_winning_move("O")
        if winning_move is not None:
            self.make_move(winning_move)
            return True

        # Block player's winning move
        blocking_move = self.get_winning_move("X")
        if blocking_move is not None:
            self.make_move(blocking_move)
            return True

        # Make a strategic move
        strategic_move = self.get_strategic_move()
        if strategic_move is not None:
            self.make_move(strategic_move)
            return True

        return False

    def get_button_grid(self) -> list:
        """
        Convert the game state into a 3x3 button grid for the chatbot
        Returns a list of button rows suitable for the chatbot client
        """
        button_rows = []
        symbols = {"X": "❌", "O": "⭕", "-": "➖"}

        # Create 3 rows of buttons
        for row in range(3):
            row_buttons = []
            for col in range(3):
                position = row * 3 + col
                symbol = symbols[self.board[position]]

                # Create button data
                button_data = {
                    "caption": symbol,
                    "action": {
                        "get_dynamic_action": {
                            "data": {
                                "game_id": str(self.id),
                                "position": str(position),
                                "action": "move",
                                "disabled": str(self.board[position] != "-"),
                            }
                        }
                    },
                }

                # If the position is already taken or game is not in progress,
                # make the button non-interactive

                row_buttons.append(button_data)

            button_rows.append({"buttons": row_buttons})

        return button_rows
