# Kenar XO Game Bot

A Tic-tac-toe (XO) chatbot built using Kenar APIs. Play the classic game against an AI opponent directly in your divar chat!

## Disclaimer
I created this chatbot for divar kenar APIs demo in only 3 hours, so it don't expect it to be clean and performant.

## 🎮 Features

- Interactive 3x3 game board with emoji buttons
- Play against an AI opponent
- Real-time game state updates
- Simple commands like `/restart` to start fresh
- Smart AI that:
  - Tries to win when possible
  - Blocks player's winning moves
  - Makes strategic moves

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Django
- Kenar API access (API key)

### Installation

1. Clone the repository
2. Serve using ngrok or your domain
3. Setup your app for chatbot according to [kenar-docs](https://github.com/divar-ir/kenar-docs)
4. Set domain/xo/webhook for session init url (back to back redirect url) and /chatbot/webhook/  for event urls in [kenar panel](https://divar.ir/kenar)

