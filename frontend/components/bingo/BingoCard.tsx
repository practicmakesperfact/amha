import { cn } from '@/lib/utils/cn'
import { getColumnLetter } from '@/lib/utils/format'

interface BingoCardProps {
  numbers: number[][] // 5x5 grid
  calledNumbers: Set<number>
  className?: string
}

export function BingoCard({ numbers, calledNumbers, className }: BingoCardProps) {
  const columns = ['B', 'I', 'N', 'G', 'O']

  const isCalled = (num: number) => calledNumbers.has(num)
  const isFree = (rowIndex: number, colIndex: number) => rowIndex === 2 && colIndex === 2

  return (
    <div className={cn('bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-4', className)}>
      {/* Header - B I N G O */}
      <div className="grid grid-cols-5 gap-1 mb-2">
        {columns.map((letter, idx) => (
          <div
            key={letter}
            className={cn(
              'text-center font-bold text-2xl py-2 rounded-lg',
              idx === 0 && 'bg-red-500 text-white',
              idx === 1 && 'bg-blue-500 text-white',
              idx === 2 && 'bg-green-500 text-white',
              idx === 3 && 'bg-yellow-500 text-white',
              idx === 4 && 'bg-purple-500 text-white'
            )}
          >
            {letter}
          </div>
        ))}
      </div>

      {/* Grid - 5x5 Numbers */}
      <div className="grid grid-cols-5 gap-1">
        {numbers.map((row, rowIndex) =>
          row.map((num, colIndex) => {
            const free = isFree(rowIndex, colIndex)
            const called = isCalled(num)
            const column = columns[colIndex]

            return (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={cn(
                  'aspect-square flex items-center justify-center rounded-lg font-bold text-lg transition-all duration-200',
                  free &&
                    'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white shadow-lg scale-105',
                  !free && !called && 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                  !free && called && 'bg-gradient-to-br from-green-500 to-green-600 text-white shadow-lg scale-105 ring-2 ring-green-400'
                )}
              >
                {free ? (
                  <span className="text-sm font-extrabold">FREE</span>
                ) : (
                  <span className={cn(called && 'animate-pulse')}>{num}</span>
                )}
              </div>
            )
          })
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 flex items-center justify-center gap-4 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-gray-200 dark:bg-gray-700" />
          <span className="text-muted-foreground">Not Called</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-green-500" />
          <span className="text-muted-foreground">Called</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-yellow-500" />
          <span className="text-muted-foreground">Free</span>
        </div>
      </div>
    </div>
  )
}
