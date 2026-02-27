const DICE_FACES = {
  1: [[1, 1]],
  2: [[0, 0], [2, 2]],
  3: [[0, 0], [1, 1], [2, 2]],
  4: [[0, 0], [0, 2], [2, 0], [2, 2]],
  5: [[0, 0], [0, 2], [1, 1], [2, 0], [2, 2]],
  6: [[0, 0], [0, 2], [1, 0], [1, 2], [2, 0], [2, 2]],
}

function Dice({ value, rolling, canRoll, onRoll }) {
  const dots = DICE_FACES[value] || DICE_FACES[1]

  return (
    <div className="flex flex-col items-center gap-4">
      <button
        onClick={onRoll}
        disabled={!canRoll}
        className={`relative w-24 h-24 bg-white rounded-2xl shadow-lg transition-all transform ${
          rolling ? 'dice-rolling' : ''
        } ${
          canRoll 
            ? 'hover:scale-110 cursor-pointer hover:shadow-xl' 
            : 'opacity-70 cursor-not-allowed'
        }`}
      >
        <div className="absolute inset-0 grid grid-cols-3 grid-rows-3 p-3">
          {Array.from({ length: 9 }).map((_, i) => {
            const row = Math.floor(i / 3)
            const col = i % 3
            const hasDot = dots.some(([r, c]) => r === row && c === col)
            
            return (
              <div key={i} className="flex items-center justify-center">
                {hasDot && (
                  <div className="w-4 h-4 bg-gray-800 rounded-full" />
                )}
              </div>
            )
          })}
        </div>
      </button>
      
      <p className="text-gray-400 text-sm">
        {canRoll ? 'Click to roll!' : rolling ? 'Rolling...' : `Rolled: ${value}`}
      </p>
    </div>
  )
}

export default Dice
