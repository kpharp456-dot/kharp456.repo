import { useState, useEffect } from 'react'
import Board from './Board'
import Dice from './Dice'
import PlayerList from './PlayerList'

function Game({ 
  gameState, 
  playerId, 
  playerName,
  roomCode, 
  onStartGame, 
  onRollDice, 
  onMovePiece,
  onLeaveRoom,
  error 
}) {
  const [copied, setCopied] = useState(false)

  const copyRoomCode = () => {
    navigator.clipboard.writeText(roomCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!gameState) {
    return (
      <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 text-center">
        <div className="animate-spin text-4xl mb-4">🎲</div>
        <p className="text-white">Connecting...</p>
      </div>
    )
  }

  const isHost = gameState.players[0]?.id === playerId
  const isMyTurn = gameState.currentPlayer === playerId
  const myPlayerIndex = gameState.players.findIndex(p => p.id === playerId)
  const currentPlayerName = gameState.players.find(p => p.id === gameState.currentPlayer)?.name || 'Unknown'

  return (
    <div className="w-full max-w-6xl">
      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-4 text-center">
          {error}
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-6 items-start">
        {/* Left Panel - Players & Controls */}
        <div className="w-full lg:w-64 space-y-4">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400 text-sm">Room Code</span>
              <button
                onClick={copyRoomCode}
                className="text-xs bg-white/20 px-2 py-1 rounded text-white hover:bg-white/30 transition"
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <div className="text-3xl font-bold text-white tracking-widest text-center">
              {roomCode}
            </div>
          </div>

          <PlayerList 
            players={gameState.players} 
            currentPlayer={gameState.currentPlayer}
            playerId={playerId}
            gameStarted={gameState.started}
          />

          {!gameState.started && (
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4 space-y-3">
              <p className="text-gray-300 text-sm text-center">
                {gameState.players.length < 2 
                  ? 'Waiting for more players...' 
                  : isHost 
                    ? 'Ready to start!' 
                    : 'Waiting for host to start...'}
              </p>
              {isHost && gameState.players.length >= 2 && (
                <button
                  onClick={onStartGame}
                  className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-xl hover:from-green-600 hover:to-emerald-700 transition transform hover:scale-105"
                >
                  Start Game
                </button>
              )}
            </div>
          )}

          <button
            onClick={onLeaveRoom}
            className="w-full py-2 bg-red-500/20 text-red-300 rounded-xl hover:bg-red-500/30 transition text-sm"
          >
            Leave Room
          </button>
        </div>

        {/* Center - Game Board */}
        <div className="flex-1 flex flex-col items-center">
          {gameState.started ? (
            <>
              <div className="mb-4 text-center">
                {gameState.winner ? (
                  <div className="text-2xl font-bold text-yellow-400">
                    🎉 {gameState.players.find(p => p.id === gameState.winner)?.name} wins! 🎉
                  </div>
                ) : (
                  <div className="text-xl text-white">
                    {isMyTurn ? (
                      <span className="text-green-400 font-bold">Your turn!</span>
                    ) : (
                      <span>{currentPlayerName}'s turn</span>
                    )}
                  </div>
                )}
              </div>

              <Board 
                gameState={gameState}
                playerId={playerId}
                myPlayerIndex={myPlayerIndex}
                onMovePiece={onMovePiece}
                isMyTurn={isMyTurn}
              />

              {!gameState.winner && (
                <div className="mt-6">
                  <Dice 
                    value={gameState.diceValue}
                    rolling={gameState.rolling}
                    canRoll={isMyTurn && !gameState.rolled && !gameState.rolling}
                    onRoll={onRollDice}
                  />
                  {isMyTurn && gameState.rolled && !gameState.hasValidMove && (
                    <p className="text-gray-400 text-center mt-2">No valid moves. Turn passes...</p>
                  )}
                </div>
              )}
            </>
          ) : (
            <div className="bg-white/5 rounded-3xl p-12 text-center">
              <div className="text-6xl mb-4">🎲</div>
              <h2 className="text-2xl font-bold text-white mb-2">Waiting for Players</h2>
              <p className="text-gray-400">
                Share the room code with your friends!
              </p>
              <p className="text-gray-500 text-sm mt-4">
                {gameState.players.length}/4 players joined
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Game
