'use client'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils/cn'

interface WinnerModalProps {
  isOpen: boolean
  isWinner: boolean
  winnerName?: string
  prizeAmount?: number
  winningPattern?: string
  onClose: () => void
}

export function WinnerModal({
  isOpen,
  isWinner,
  winnerName,
  prizeAmount,
  winningPattern,
  onClose,
}: WinnerModalProps) {
  const [confetti, setConfetti] = useState(false)

  useEffect(() => {
    if (isOpen && isWinner) {
      setConfetti(true)
      const timer = setTimeout(() => setConfetti(false), 5000)
      return () => clearTimeout(timer)
    }
  }, [isOpen, isWinner])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative max-w-md w-full mx-4 bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 text-center">
        {/* Confetti Effect */}
        {confetti && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {Array.from({ length: 50 }).map((_, i) => (
              <div
                key={i}
                className="absolute w-2 h-2 bg-gradient-to-r from-yellow-400 to-red-500 rounded-full animate-confetti"
                style={{
                  left: `${Math.random() * 100}%`,
                  top: '-10px',
                  animationDelay: `${Math.random() * 2}s`,
                }}
              />
            ))}
          </div>
        )}

        {isWinner ? (
          <>
            <div className="text-8xl mb-4 animate-bounce">🏆</div>
            <h2 className="text-4xl font-bold mb-2 text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">
              BINGO!
            </h2>
            <p className="text-2xl font-bold mb-4 text-green-600">You Won!</p>
            {prizeAmount && (
              <div className="mb-4">
                <p className="text-sm text-muted-foreground mb-1">Prize</p>
                <p className="text-4xl font-extrabold text-green-600">
                  {prizeAmount.toFixed(2)} ETB
                </p>
              </div>
            )}
            {winningPattern && (
              <div className="mb-6">
                <p className="text-sm text-muted-foreground mb-1">Winning Pattern</p>
                <p className="text-lg font-semibold capitalize">{winningPattern}</p>
              </div>
            )}
            <p className="text-sm text-muted-foreground mb-6">
              🎉 Congratulations! Your prize has been credited to your wallet.
            </p>
          </>
        ) : (
          <>
            <div className="text-8xl mb-4">🎊</div>
            <h2 className="text-3xl font-bold mb-2">Game Finished!</h2>
            {winnerName && (
              <p className="text-lg mb-4">
                Winner: <span className="font-bold">{winnerName}</span>
              </p>
            )}
            {prizeAmount && (
              <p className="text-sm text-muted-foreground mb-6">
                Prize: {prizeAmount.toFixed(2)} ETB
              </p>
            )}
            <p className="text-sm text-muted-foreground mb-6">
              Better luck next time! Try again in the next game.
            </p>
          </>
        )}

        <Button onClick={onClose} variant="primary" size="lg" className="w-full">
          {isWinner ? '🎉 Awesome!' : 'Play Again'}
        </Button>
      </div>
    </div>
  )
}

// Add this to your globals.css for confetti animation
// @keyframes confetti {
//   0% { transform: translateY(0) rotate(0deg); opacity: 1; }
//   100% { transform: translateY(100vh) rotate(720deg); opacity: 0; }
// }
// .animate-confetti {
//   animation: confetti 3s ease-out forwards;
// }
