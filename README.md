# 🎲 Ludo - Multiplayer Board Game

A real-time multiplayer Ludo game to play with friends online!

## Features

- **Real-time multiplayer** - Play with 2-4 friends from anywhere
- **Room codes** - Easy to share and join games
- **Classic Ludo rules** - Roll a 6 to leave home, capture opponents, race to finish
- **Beautiful UI** - Modern, responsive design

## Quick Start

### 1. Install dependencies
```bash
npm install
```

### 2. Start the game
```bash
npm run dev
```

This starts both the server (port 3001) and client (port 5173).

### 3. Open in browser
Navigate to `http://localhost:5173`

### 4. Play!
1. Enter your name
2. Create a new game or join with a room code
3. Share the room code with friends
4. Host starts the game when everyone's ready

## Game Rules

- **Starting**: Roll a 6 to move a piece out of your home base
- **Movement**: Move pieces clockwise around the board by the dice value
- **Capture**: Land on an opponent's piece to send it back home (except on safe spots marked with ★)
- **Rolling 6**: Get another turn when you roll a 6
- **Winning**: First player to get all 4 pieces to the center wins!

## Tech Stack

- **Frontend**: React + Vite + TailwindCSS
- **Backend**: Node.js + Express + Socket.io
- **Real-time**: WebSocket communication

## Development

```bash
# Run server only
npm run server

# Run client only
npm run client

# Run both
npm run dev
```

## License

This is a personal project for playing with friends. The game mechanics are based on the public domain game Ludo/Parcheesi.
