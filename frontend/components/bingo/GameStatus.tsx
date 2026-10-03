import { cn } from '@/lib/utils/cn'

interface GameStatusProps {
  status: 'WAITING' | 'PLAYING' | 'PAUSED' | 'FINISHED' | 'CANCELLED'
  playerCount?: number
  prizePool: number
  className?: string
}

export function GameStatus({ status, playerCount, prizePool, className }: GameStatusProps) {
  const statusConfig = {
    WAITING: {
      label: 'Waiting to Start',
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      icon: '⏳',
    },
    PLAYING: {
      label: 'Live Game',
      color: 'bg-green-100 text-green-800 border-green-200',
      icon: '🎮',
    },
    PAUSED: {
      label: 'Paused',
      color: 'bg-orange-100 text-orange-800 border-orange-200',
      icon: '⏸️',
    },
    FINISHED: {
      label: 'Finished',
      color: 'bg-gray-100 text-gray-800 border-gray-200',
      icon: '🏁',
    },
    CANCELLED: {
      label: 'Cancelled',
      color: 'bg-red-100 text-red-800 border-red-200',
      icon: '❌',
    },
  }

  const config = statusConfig[status]

  return (
    <div className={cn('flex items-center justify-between p-4 rounded-lg border-2', config.color, className)}>
      <div className="flex items-center gap-2">
        <span className="text-2xl">{config.icon}</span>
        <div>
          <p className="font-bold text-sm">{config.label}</p>
          {playerCount !== undefined && (
            <p className="text-xs opacity-75">{playerCount} players</p>
          )}
        </div>
      </div>
      <div className="text-right">
        <p className="text-xs opacity-75">Prize Pool</p>
        <p className="font-bold text-lg">{prizePool.toFixed(2)} ETB</p>
      </div>
    </div>
  )
}
