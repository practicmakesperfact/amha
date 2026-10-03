import { cn } from '@/lib/utils/cn'
import { getColumnLetter } from '@/lib/utils/format'

interface CalledNumbersProps {
  numbers: number[]
  className?: string
}

export function CalledNumbers({ numbers, className }: CalledNumbersProps) {
  if (numbers.length === 0) {
    return (
      <div className={cn('text-center py-4', className)}>
        <p className="text-sm text-muted-foreground">No numbers called yet</p>
      </div>
    )
  }

  const columnColors = {
    B: 'bg-red-500',
    I: 'bg-blue-500',
    N: 'bg-green-500',
    G: 'bg-yellow-500',
    O: 'bg-purple-500',
  }

  // Show in reverse order (most recent first)
  const reversedNumbers = [...numbers].reverse()

  return (
    <div className={cn('', className)}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-sm">Called Numbers</h3>
        <span className="text-xs text-muted-foreground">{numbers.length} / 75</span>
      </div>
      
      <div className="grid grid-cols-8 gap-2 max-h-48 overflow-y-auto p-2 bg-gray-50 dark:bg-gray-900 rounded-lg">
        {reversedNumbers.map((num, idx) => {
          const column = getColumnLetter(num)
          const isLatest = idx === 0
          
          return (
            <div
              key={`${num}-${idx}`}
              className={cn(
                'aspect-square flex items-center justify-center rounded-lg text-white font-bold text-sm transition-all',
                columnColors[column],
                isLatest && 'ring-2 ring-offset-2 ring-white scale-110 animate-pulse'
              )}
            >
              {num}
            </div>
          )
        })}
      </div>
    </div>
  )
}
