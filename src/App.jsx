import { useState, useEffect } from 'react'
import { io } from 'socket.io-client'
import Lobby from './components/Lobby'
import Game from './components/Game'

const socket = io('http://localhost:3001')

function App() {
  const [gameState, setGameState] = useState(null)
  const [playerId, setPlayerId] = useState(null)
  const [roomCode, setRoomCode] = useState(null)
  const [error, setError] = useState(null)
  const [playerName, setPlayerName] = useState('')

  useEffect(() => {
    socket.on('connect', () => {
      setPlayerId(socket.id)
    })

    socket.on('gameState', (state) => {
      setGameState(state)
      setError(null)
    })

    socket.on('roomJoined', ({ roomCode }) => {
      setRoomCode(roomCode)
    })

    socket.on('error', (message) => {
      setError(message)
    })

    return () => {
      socket.off('connect')
      socket.off('gameState')
      socket.off('roomJoined')
      socket.off('error')
    }
  }, [])

  const createRoom = (name) => {
    setPlayerName(name)
    socket.emit('createRoom', { playerName: name })
  }

  const joinRoom = (code, name) => {
    setPlayerName(name)
    socket.emit('joinRoom', { roomCode: code, playerName: name })
  }

  const startGame = () => {
    socket.emit('startGame', { roomCode })
  }

  const rollDice = () => {
    socket.emit('rollDice', { roomCode })
  }

  const movePiece = (pieceIndex) => {
    socket.emit('movePiece', { roomCode, pieceIndex })
  }

  const leaveRoom = () => {
    socket.emit('leaveRoom', { roomCode })
    setRoomCode(null)
    setGameState(null)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {!roomCode ? (
        <Lobby 
          onCreateRoom={createRoom} 
          onJoinRoom={joinRoom} 
          error={error}
        />
      ) : (
        <Game 
          gameState={gameState}
          playerId={playerId}
          playerName={playerName}
          roomCode={roomCode}
          onStartGame={startGame}
          onRollDice={rollDice}
          onMovePiece={movePiece}
          onLeaveRoom={leaveRoom}
          error={error}
        />
      )}
    </div>
  )
}

export default App
