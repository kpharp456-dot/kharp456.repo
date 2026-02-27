import { useMemo } from 'react'

const PLAYER_COLORS = ['#ef4444', '#3b82f6', '#22c55e', '#eab308']
const PLAYER_BG_COLORS = ['bg-red-500', 'bg-blue-500', 'bg-green-500', 'bg-yellow-500']
const PLAYER_LIGHT_BG = ['bg-red-200', 'bg-blue-200', 'bg-green-200', 'bg-yellow-200']

const BOARD_SIZE = 15
const CELL_SIZE = 32

const PATH_LENGTH = 52
const HOME_STRETCH_LENGTH = 5

function generatePath() {
  const path = []
  
  for (let i = 0; i < 6; i++) path.push({ row: 6, col: i })
  path.push({ row: 6, col: 6 })
  for (let i = 5; i >= 0; i--) path.push({ row: i, col: 6 })
  path.push({ row: 0, col: 7 })
  path.push({ row: 0, col: 8 })
  for (let i = 1; i <= 6; i++) path.push({ row: i, col: 8 })
  path.push({ row: 6, col: 8 })
  for (let i = 9; i <= 14; i++) path.push({ row: 6, col: i })
  path.push({ row: 7, col: 14 })
  path.push({ row: 8, col: 14 })
  for (let i = 13; i >= 8; i--) path.push({ row: 8, col: i })
  path.push({ row: 8, col: 8 })
  for (let i = 9; i <= 14; i++) path.push({ row: i, col: 8 })
  path.push({ row: 14, col: 7 })
  path.push({ row: 14, col: 6 })
  for (let i = 13; i >= 8; i--) path.push({ row: i, col: 6 })
  path.push({ row: 8, col: 6 })
  for (let i = 5; i >= 0; i--) path.push({ row: 8, col: i })
  path.push({ row: 7, col: 0 })
  
  return path
}

const MAIN_PATH = generatePath()

const HOME_STRETCHES = [
  Array.from({ length: 5 }, (_, i) => ({ row: 7, col: 1 + i })),
  Array.from({ length: 5 }, (_, i) => ({ row: 1 + i, col: 7 })),
  Array.from({ length: 5 }, (_, i) => ({ row: 7, col: 13 - i })),
  Array.from({ length: 5 }, (_, i) => ({ row: 13 - i, col: 7 })),
]

const START_POSITIONS = [0, 13, 26, 39]

const HOME_BASES = [
  [{ row: 1, col: 1 }, { row: 1, col: 4 }, { row: 4, col: 1 }, { row: 4, col: 4 }],
  [{ row: 1, col: 10 }, { row: 1, col: 13 }, { row: 4, col: 10 }, { row: 4, col: 13 }],
  [{ row: 10, col: 10 }, { row: 10, col: 13 }, { row: 13, col: 10 }, { row: 13, col: 13 }],
  [{ row: 10, col: 1 }, { row: 10, col: 4 }, { row: 13, col: 1 }, { row: 13, col: 4 }],
]

const SAFE_SPOTS = [0, 8, 13, 21, 26, 34, 39, 47]

function Board({ gameState, playerId, myPlayerIndex, onMovePiece, isMyTurn }) {
  const grid = useMemo(() => {
    const g = Array(BOARD_SIZE).fill(null).map(() => 
      Array(BOARD_SIZE).fill(null).map(() => ({ type: 'empty', color: null }))
    )

    for (let pi = 0; pi < 4; pi++) {
      const baseColor = pi
      HOME_BASES[pi].forEach(({ row, col }) => {
        g[row][col] = { type: 'home-base', color: baseColor }
      })
      
      for (let r = (pi < 2 ? 0 : 9); r < (pi < 2 ? 6 : 15); r++) {
        for (let c = (pi % 2 === 0 ? 0 : 9); c < (pi % 2 === 0 ? 6 : 15); c++) {
          if (g[r][c].type === 'empty') {
            g[r][c] = { type: 'home-area', color: baseColor }
          }
        }
      }
    }

    MAIN_PATH.forEach(({ row, col }, idx) => {
      const isSafe = SAFE_SPOTS.includes(idx)
      g[row][col] = { type: 'path', color: null, safe: isSafe, pathIndex: idx }
    })

    HOME_STRETCHES.forEach((stretch, playerIdx) => {
      stretch.forEach(({ row, col }, idx) => {
        g[row][col] = { type: 'home-stretch', color: playerIdx, stretchIndex: idx }
      })
    })

    g[7][7] = { type: 'center', color: null }

    return g
  }, [])

  const getPiecePosition = (playerIndex, piece) => {
    if (piece.finished) {
      return { row: 7, col: 7, inCenter: true }
    }
    if (piece.position === -1) {
      return HOME_BASES[playerIndex][piece.homeSlot || 0]
    }
    if (piece.inHomeStretch) {
      return HOME_STRETCHES[playerIndex][piece.homeStretchPosition]
    }
    const actualPosition = (START_POSITIONS[playerIndex] + piece.position) % PATH_LENGTH
    return MAIN_PATH[actualPosition]
  }

  const canMovePiece = (playerIndex, pieceIndex) => {
    if (!isMyTurn || !gameState.rolled || playerIndex !== myPlayerIndex) return false
    const piece = gameState.players[playerIndex].pieces[pieceIndex]
    if (piece.finished) return false
    
    const diceValue = gameState.diceValue
    
    if (piece.position === -1) {
      return diceValue === 6
    }
    
    return true
  }

  const renderCell = (row, col) => {
    const cell = grid[row][col]
    let bgColor = 'bg-gray-700'
    let borderColor = 'border-gray-600'

    if (cell.type === 'home-area') {
      bgColor = PLAYER_LIGHT_BG[cell.color] + '/30'
    } else if (cell.type === 'home-base') {
      bgColor = PLAYER_LIGHT_BG[cell.color]
    } else if (cell.type === 'path') {
      bgColor = cell.safe ? 'bg-gray-400' : 'bg-gray-200'
    } else if (cell.type === 'home-stretch') {
      bgColor = PLAYER_LIGHT_BG[cell.color]
    } else if (cell.type === 'center') {
      bgColor = 'bg-gradient-to-br from-red-400 via-blue-400 to-green-400'
    }

    const piecesHere = []
    gameState.players.forEach((player, playerIndex) => {
      player.pieces.forEach((piece, pieceIndex) => {
        const pos = getPiecePosition(playerIndex, piece)
        if (pos.row === row && pos.col === col && !pos.inCenter) {
          piecesHere.push({ playerIndex, pieceIndex, piece })
        }
      })
    })

    return (
      <div
        key={`${row}-${col}`}
        className={`w-8 h-8 ${bgColor} border ${borderColor} flex items-center justify-center relative`}
        style={{ fontSize: '10px' }}
      >
        {cell.safe && cell.type === 'path' && (
          <span className="absolute text-gray-500 text-xs">★</span>
        )}
        {piecesHere.map(({ playerIndex, pieceIndex, piece }, idx) => {
          const canMove = canMovePiece(playerIndex, pieceIndex)
          return (
            <button
              key={`${playerIndex}-${pieceIndex}`}
              onClick={() => canMove && onMovePiece(pieceIndex)}
              disabled={!canMove}
              className={`absolute w-5 h-5 rounded-full border-2 border-white shadow-md transition-all ${
                canMove ? 'cursor-pointer hover:scale-125 animate-pulse ring-2 ring-white' : ''
              }`}
              style={{
                backgroundColor: PLAYER_COLORS[playerIndex],
                transform: piecesHere.length > 1 ? `translate(${(idx - 0.5) * 8}px, ${(idx - 0.5) * 8}px)` : undefined,
                zIndex: canMove ? 10 : 1,
              }}
            />
          )
        })}
      </div>
    )
  }

  const finishedPieces = gameState.players.flatMap((player, playerIndex) =>
    player.pieces.filter(p => p.finished).map(() => playerIndex)
  )

  return (
    <div className="bg-gray-800 p-2 rounded-2xl shadow-2xl">
      <div 
        className="grid gap-0"
        style={{ 
          gridTemplateColumns: `repeat(${BOARD_SIZE}, ${CELL_SIZE}px)`,
          gridTemplateRows: `repeat(${BOARD_SIZE}, ${CELL_SIZE}px)`,
        }}
      >
        {Array.from({ length: BOARD_SIZE }).map((_, row) =>
          Array.from({ length: BOARD_SIZE }).map((_, col) => renderCell(row, col))
        )}
      </div>
      
      {finishedPieces.length > 0 && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex gap-1">
          {finishedPieces.map((playerIndex, idx) => (
            <div
              key={idx}
              className="w-4 h-4 rounded-full border border-white"
              style={{ backgroundColor: PLAYER_COLORS[playerIndex] }}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default Board
