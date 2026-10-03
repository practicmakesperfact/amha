import { cn } from '@/lib/utils/cn'

interface ConnectionStatusProps {
  status: 'connecting' | 'connected' | 'disconnected'
  className?: string
}

export function ConnectionStatus({ status, className }: ConnectionStatusProps) {
  const statusConfig = {
    connecting: {
      label: 'Connecting...',
      color: 'bg-yellow-500',
      textColor: 'text-yellow-700',
      icon: '🔄',
    },
    connected: {
      label: 'Connected',
      color: 'bg-green-500',
      textColor: 'text-green-700',
      icon: '✓',
    },
    disconnected: {
      label: 'Disconnected',
      color: 'bg-red-500',
      textColor: 'text-red-700',
      icon: '✗',
    },
  }

  const config = statusConfig[status]

  if (status === 'connected') {
    // Don't show when connected (clutter-free)
    return null
  }

  return (
    <div className={cn('flex items-center gap-2 text-sm', config.textColor, className)}>
      <div className={cn('w-2 h-2 rounded-full', config.color, status === 'connecting' && 'animate-pulse')} />
      <span className="font-medium">{config.label}</span>
      {status === 'disconnected' && (
        <span className="text-xs opacity-75">Reconnecting...</span>
      )}
    </div>
  )
}
