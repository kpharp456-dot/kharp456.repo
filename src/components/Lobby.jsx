import { useState } from 'react'

function Lobby({ onCreateRoom, onJoinRoom, error }) {
  const [name, setName] = useState('')
  const [joinCode, setJoinCode] = useState('')
  const [mode, setMode] = useState('menu')

  const handleCreate = (e) => {
    e.preventDefault()
    if (name.trim()) {
      onCreateRoom(name.trim())
    }
  }

  const handleJoin = (e) => {
    e.preventDefault()
    if (name.trim() && joinCode.trim()) {
      onJoinRoom(joinCode.trim().toUpperCase(), name.trim())
    }
  }

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 w-full max-w-md shadow-2xl">
      <div className="text-center mb-8">
        <h1 className="text-5xl font-bold text-white mb-2">🎲 Ludo</h1>
        <p className="text-gray-300">Play with friends anywhere!</p>
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {mode === 'menu' && (
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-3 rounded-xl bg-white/20 text-white placeholder-gray-400 border border-white/30 focus:outline-none focus:border-white/60 transition"
            maxLength={20}
          />
          <button
            onClick={() => name.trim() && setMode('create')}
            disabled={!name.trim()}
            className="w-full py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-xl hover:from-green-600 hover:to-emerald-700 transition transform hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
          >
            Create New Game
          </button>
          <button
            onClick={() => name.trim() && setMode('join')}
            disabled={!name.trim()}
            className="w-full py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold rounded-xl hover:from-blue-600 hover:to-indigo-700 transition transform hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
          >
            Join Game
          </button>
        </div>
      )}

      {mode === 'create' && (
        <form onSubmit={handleCreate} className="space-y-4">
          <p className="text-gray-300 text-center">
            Ready to create a game as <span className="text-white font-bold">{name}</span>?
          </p>
          <button
            type="submit"
            className="w-full py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-xl hover:from-green-600 hover:to-emerald-700 transition transform hover:scale-105"
          >
            Create Room
          </button>
          <button
            type="button"
            onClick={() => setMode('menu')}
            className="w-full py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition"
          >
            Back
          </button>
        </form>
      )}

      {mode === 'join' && (
        <form onSubmit={handleJoin} className="space-y-4">
          <input
            type="text"
            placeholder="Enter room code"
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
            className="w-full px-4 py-3 rounded-xl bg-white/20 text-white placeholder-gray-400 border border-white/30 focus:outline-none focus:border-white/60 transition text-center text-2xl tracking-widest"
            maxLength={6}
          />
          <button
            type="submit"
            disabled={!joinCode.trim()}
            className="w-full py-4 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold rounded-xl hover:from-blue-600 hover:to-indigo-700 transition transform hover:scale-105 disabled:opacity-50"
          >
            Join Room
          </button>
          <button
            type="button"
            onClick={() => setMode('menu')}
            className="w-full py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition"
          >
            Back
          </button>
        </form>
      )}
    </div>
  )
}

export default Lobby
