import express from 'express'
import { createServer } from 'http'
import { Server } from 'socket.io'
import { v4 as uuidv4 } from 'uuid'

const app = express()
const server = createServer(app)
const io = new Server(server, {
  cors: {
    origin: "http://localhost:5173",
    methods: ["GET", "POST"]
  }
})

const rooms = new Map()

function generateRoomCode() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let code = ''
  for (let i = 0; i < 5; i++) {
    code += chars[Math.floor(Math.random() * chars.length)]
  }
  return code
}

function createInitialPieces() {
  return [
    { position: -1, inHomeStretch: false, homeStretchPosition: 0, finished: false, homeSlot: 0 },
    { position: -1, inHomeStretch: false, homeStretchPosition: 0, finished: false, homeSlot: 1 },
    { position: -1, inHomeStretch: false, homeStretchPosition: 0, finished: false, homeSlot: 2 },
    { position: -1, inHomeStretch: false, homeStretchPosition: 0, finished: false, homeSlot: 3 },
  ]
}

function createRoom(hostId, hostName) {
  let code = generateRoomCode()
  while (rooms.has(code)) {
    code = generateRoomCode()
  }

  const room = {
    code,
    players: [{
      id: hostId,
      name: hostName,
      pieces: createInitialPieces(),
    }],
    started: false,
    currentPlayer: null,
    currentPlayerIndex: 0,
    diceValue: 1,
    rolled: false,
    rolling: false,
    winner: null,
    hasValidMove: true,
  }

  rooms.set(code, room)
  return room
}

function getRoom(code) {
  return rooms.get(code)
}

function rollDice() {
  return Math.floor(Math.random() * 6) + 1
}

const PATH_LENGTH = 52
const HOME_STRETCH_LENGTH = 5
const SAFE_SPOTS = [0, 8, 13, 21, 26, 34, 39, 47]

function canPieceMove(piece, diceValue, playerIndex, room) {
  if (piece.finished) return false

  if (piece.position === -1) {
    return diceValue === 6
  }

  if (piece.inHomeStretch) {
    const newPos = piece.homeStretchPosition + diceValue
    return newPos <= HOME_STRETCH_LENGTH
  }

  const stepsToHome = PATH_LENGTH - piece.position
  if (diceValue > stepsToHome + HOME_STRETCH_LENGTH) {
    return false
  }

  return true
}

function hasAnyValidMove(player, diceValue, playerIndex, room) {
  return player.pieces.some(piece => canPieceMove(piece, diceValue, playerIndex, room))
}

function movePiece(room, playerIndex, pieceIndex) {
  const player = room.players[playerIndex]
  const piece = player.pieces[pieceIndex]
  const diceValue = room.diceValue

  if (!canPieceMove(piece, diceValue, playerIndex, room)) {
    return { success: false, message: 'Invalid move' }
  }

  if (piece.position === -1) {
    piece.position = 0
    checkCapture(room, playerIndex, pieceIndex)
    return { success: true, rolled6: true }
  }

  if (piece.inHomeStretch) {
    piece.homeStretchPosition += diceValue
    if (piece.homeStretchPosition >= HOME_STRETCH_LENGTH) {
      piece.finished = true
      piece.homeStretchPosition = HOME_STRETCH_LENGTH
    }
    return { success: true, rolled6: diceValue === 6 }
  }

  const newPosition = piece.position + diceValue
  
  if (newPosition >= PATH_LENGTH) {
    piece.inHomeStretch = true
    piece.homeStretchPosition = newPosition - PATH_LENGTH
    if (piece.homeStretchPosition >= HOME_STRETCH_LENGTH) {
      piece.finished = true
      piece.homeStretchPosition = HOME_STRETCH_LENGTH
    }
  } else {
    piece.position = newPosition
    checkCapture(room, playerIndex, pieceIndex)
  }

  return { success: true, rolled6: diceValue === 6 }
}

function checkCapture(room, movingPlayerIndex, movingPieceIndex) {
  const movingPlayer = room.players[movingPlayerIndex]
  const movingPiece = movingPlayer.pieces[movingPieceIndex]
  
  if (movingPiece.position === -1 || movingPiece.inHomeStretch) return

  const START_POSITIONS = [0, 13, 26, 39]
  const movingAbsolutePos = (START_POSITIONS[movingPlayerIndex] + movingPiece.position) % PATH_LENGTH

  if (SAFE_SPOTS.includes(movingAbsolutePos)) return

  room.players.forEach((player, playerIndex) => {
    if (playerIndex === movingPlayerIndex) return

    player.pieces.forEach((piece, pieceIndex) => {
      if (piece.position === -1 || piece.inHomeStretch || piece.finished) return

      const pieceAbsolutePos = (START_POSITIONS[playerIndex] + piece.position) % PATH_LENGTH
      
      if (pieceAbsolutePos === movingAbsolutePos) {
        piece.position = -1
        piece.homeSlot = pieceIndex
      }
    })
  })
}

function checkWinner(room) {
  for (const player of room.players) {
    if (player.pieces.every(piece => piece.finished)) {
      return player.id
    }
  }
  return null
}

function nextTurn(room, rolled6 = false) {
  if (rolled6) {
    room.rolled = false
    room.hasValidMove = true
    return
  }

  room.currentPlayerIndex = (room.currentPlayerIndex + 1) % room.players.length
  room.currentPlayer = room.players[room.currentPlayerIndex].id
  room.rolled = false
  room.hasValidMove = true
}

function broadcastGameState(roomCode) {
  const room = getRoom(roomCode)
  if (room) {
    io.to(roomCode).emit('gameState', room)
  }
}

io.on('connection', (socket) => {
  console.log('Player connected:', socket.id)

  socket.on('createRoom', ({ playerName }) => {
    const room = createRoom(socket.id, playerName)
    socket.join(room.code)
    socket.emit('roomJoined', { roomCode: room.code })
    broadcastGameState(room.code)
    console.log(`Room ${room.code} created by ${playerName}`)
  })

  socket.on('joinRoom', ({ roomCode, playerName }) => {
    const room = getRoom(roomCode)
    
    if (!room) {
      socket.emit('error', 'Room not found')
      return
    }

    if (room.started) {
      socket.emit('error', 'Game already started')
      return
    }

    if (room.players.length >= 4) {
      socket.emit('error', 'Room is full')
      return
    }

    if (room.players.some(p => p.id === socket.id)) {
      socket.emit('error', 'Already in room')
      return
    }

    room.players.push({
      id: socket.id,
      name: playerName,
      pieces: createInitialPieces(),
    })

    socket.join(roomCode)
    socket.emit('roomJoined', { roomCode })
    broadcastGameState(roomCode)
    console.log(`${playerName} joined room ${roomCode}`)
  })

  socket.on('startGame', ({ roomCode }) => {
    const room = getRoom(roomCode)
    
    if (!room) {
      socket.emit('error', 'Room not found')
      return
    }

    if (room.players[0].id !== socket.id) {
      socket.emit('error', 'Only host can start the game')
      return
    }

    if (room.players.length < 2) {
      socket.emit('error', 'Need at least 2 players')
      return
    }

    room.started = true
    room.currentPlayerIndex = 0
    room.currentPlayer = room.players[0].id
    
    broadcastGameState(roomCode)
    console.log(`Game started in room ${roomCode}`)
  })

  socket.on('rollDice', ({ roomCode }) => {
    const room = getRoom(roomCode)
    
    if (!room || !room.started) {
      socket.emit('error', 'Game not started')
      return
    }

    if (room.currentPlayer !== socket.id) {
      socket.emit('error', 'Not your turn')
      return
    }

    if (room.rolled) {
      socket.emit('error', 'Already rolled')
      return
    }

    room.rolling = true
    broadcastGameState(roomCode)

    setTimeout(() => {
      room.diceValue = rollDice()
      room.rolled = true
      room.rolling = false

      const playerIndex = room.players.findIndex(p => p.id === socket.id)
      room.hasValidMove = hasAnyValidMove(room.players[playerIndex], room.diceValue, playerIndex, room)

      if (!room.hasValidMove) {
        broadcastGameState(roomCode)
        setTimeout(() => {
          nextTurn(room, false)
          broadcastGameState(roomCode)
        }, 1500)
      } else {
        broadcastGameState(roomCode)
      }
    }, 500)
  })

  socket.on('movePiece', ({ roomCode, pieceIndex }) => {
    const room = getRoom(roomCode)
    
    if (!room || !room.started) {
      socket.emit('error', 'Game not started')
      return
    }

    if (room.currentPlayer !== socket.id) {
      socket.emit('error', 'Not your turn')
      return
    }

    if (!room.rolled) {
      socket.emit('error', 'Roll first')
      return
    }

    const playerIndex = room.players.findIndex(p => p.id === socket.id)
    const result = movePiece(room, playerIndex, pieceIndex)

    if (!result.success) {
      socket.emit('error', result.message)
      return
    }

    const winner = checkWinner(room)
    if (winner) {
      room.winner = winner
      broadcastGameState(roomCode)
      return
    }

    nextTurn(room, result.rolled6)
    broadcastGameState(roomCode)
  })

  socket.on('leaveRoom', ({ roomCode }) => {
    const room = getRoom(roomCode)
    if (room) {
      room.players = room.players.filter(p => p.id !== socket.id)
      socket.leave(roomCode)
      
      if (room.players.length === 0) {
        rooms.delete(roomCode)
        console.log(`Room ${roomCode} deleted (empty)`)
      } else {
        if (room.started && room.currentPlayer === socket.id) {
          nextTurn(room, false)
        }
        broadcastGameState(roomCode)
      }
    }
  })

  socket.on('disconnect', () => {
    console.log('Player disconnected:', socket.id)
    
    rooms.forEach((room, roomCode) => {
      const playerIndex = room.players.findIndex(p => p.id === socket.id)
      if (playerIndex !== -1) {
        room.players.splice(playerIndex, 1)
        
        if (room.players.length === 0) {
          rooms.delete(roomCode)
          console.log(`Room ${roomCode} deleted (empty)`)
        } else {
          if (room.started) {
            if (room.currentPlayerIndex >= room.players.length) {
              room.currentPlayerIndex = 0
            }
            room.currentPlayer = room.players[room.currentPlayerIndex].id
            room.rolled = false
          }
          broadcastGameState(roomCode)
        }
      }
    })
  })
})

const PORT = process.env.PORT || 3001
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})
