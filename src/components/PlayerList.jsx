const PLAYER_COLORS = [
  { name: 'Red', bg: 'bg-red-500', text: 'text-red-500', border: 'border-red-500' },
  { name: 'Blue', bg: 'bg-blue-500', text: 'text-blue-500', border: 'border-blue-500' },
  { name: 'Green', bg: 'bg-green-500', text: 'text-green-500', border: 'border-green-500' },
  { name: 'Yellow', bg: 'bg-yellow-500', text: 'text-yellow-500', border: 'border-yellow-500' },
]

function PlayerList({ players, currentPlayer, playerId, gameStarted }) {
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-4">
      <h3 className="text-white font-bold mb-3">Players</h3>
      <div className="space-y-2">
        {players.map((player, index) => {
          const color = PLAYER_COLORS[index]
          const isCurrentTurn = gameStarted && player.id === currentPlayer
          const isYou = player.id === playerId
          
          return (
            <div
              key={player.id}
              className={`flex items-center gap-3 p-2 rounded-lg transition ${
                isCurrentTurn ? 'bg-white/20' : ''
              }`}
            >
              <div className={`w-4 h-4 rounded-full ${color.bg}`} />
              <span className={`flex-1 ${isCurrentTurn ? 'text-white font-bold' : 'text-gray-300'}`}>
                {player.name}
                {isYou && <span className="text-gray-500 text-xs ml-1">(you)</span>}
              </span>
              {isCurrentTurn && (
                <span className="text-xs bg-white/20 px-2 py-1 rounded text-white">
                  Playing
                </span>
              )}
              {index === 0 && !gameStarted && (
                <span className="text-xs bg-yellow-500/30 px-2 py-1 rounded text-yellow-300">
                  Host
                </span>
              )}
            </div>
          )
        })}
        
        {Array.from({ length: 4 - players.length }).map((_, i) => (
          <div key={`empty-${i}`} className="flex items-center gap-3 p-2 opacity-30">
            <div className={`w-4 h-4 rounded-full ${PLAYER_COLORS[players.length + i].bg}`} />
            <span className="text-gray-500">Waiting...</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PlayerList
