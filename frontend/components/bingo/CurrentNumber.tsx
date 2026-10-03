import { cn } from '@/lib/utils/cn'
import { getColumnLetter } from '@/lib/utils/format'

interface CurrentNumberProps {
  number: number | null
  className?: string
}

export function CurrentNumber({ number, className }: CurrentNumberProps) {
  if (!number) {
    return (
      <div className={cn('text-center py-8', className)}>
        <div className="inline-block animate-pulse">
          <div className="w-32 h-32 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
            <span className="text-4xl">🎲</span>
          </div>
          <p className="text-sm text-muted-foreground mt-4">Waiting for first number...</p>
        </div>
      </div>
    )
  }

  const column = getColumnLetter(number)
  
  const columnColors = {
    B: 'from-red-500 to-red-600',
    I: 'from-blue-500 to-blue-600',
    N: 'from-green-500 to-green-600',
    G: 'from-yellow-500 to-yellow-600',
    O: 'from-purple-500 to-purple-600',
  }

  return (
    <div className={cn('text-center py-6', className)}>
      <p className="text-sm text-muted-foreground mb-2 uppercase tracking-wider">Current Number</p>
      <div className="inline-block">
        <div
          className={cn(
            'w-40 h-40 rounded-full flex flex-col items-center justify-center shadow-2xl animate-bounce',
            'bg-gradient-to-br',
            columnColors[column]
          )}
        >
          <span className="text-2xl font-bold text-white mb-1">{column}</span>
          <span className="text-6xl font-extrabold text-white">{number}</span>
        </div>
      </div>
    </div>
  )
}
