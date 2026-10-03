'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { playerApi } from '@/lib/api/endpoints'
import { useAuth } from '@/providers/auth-provider'
import { useBingoWebSocket } from '@/hooks/useBingoWebSocket'
import { useTelegram } from '@/hooks/useTelegram'
import { BingoCard } from '@/components/bingo/BingoCard'
import { CurrentNumber } from '@/components/bingo/CurrentNumber'
import { CalledNumbers } from '@/components/bingo/CalledNumbers'
import { GameStatus } from '@/components/bingo/GameStatus'
import { ConnectionStatus } from '@/components/bingo/ConnectionStatus'
import { WinnerModal } from '@/components/bingo/WinnerModal'
import { LoadingPage } from '@/components/ui/Loading'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import Link from 'next/link'

export default function GamePage() {
  const params = useParams()
  const router = useRouter()
  const gameId = parseInt(params.id as string)
  const { user, isAuthenticated } = useAuth()
  const { hapticFeedback } = useTelegram()
  const queryClient = useQueryClient()

  const [currentNumber, setCurrentNumber] = useState<number | null>(null)
  const [calledNumbers, setCalledNumbers] = useState<number[]>([])
  const [showWinnerModal, setShowWinnerModal] = useState(false)
  const [winnerData, setWinnerData] = useState<any>(null)

  // Fetch game data
  const { data: game, isLoading: gameLoading } = useQuery({
    queryKey: ['game', gameId],
    queryFn: () => playerApi.getGame(gameId),
    enabled: isAuthenticated,
    refetchInterval: 5000,
  })

  // Fetch player's cartela
  const { data: cartela, isLoading: cartelaLoading } = useQuery({
    queryKey: ['cartela', gameId],
    queryFn: () => playerApi.getCartela(gameId),
    enabled: isAuthenticated && game?.status !== 'WAITING',
  })

  // Join game mutation
  const joinMutation = useMutation({
    mutationFn: () => playerApi.joinGame(gameId),
    onSuccess: (data) => {
      hapticFeedback('success')
      queryClient.invalidateQueries({ queryKey: ['game', gameId] })
      queryClient.invalidateQueries({ queryKey: ['cartela', gameId] })
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] })
    },
    onError: (error: any) => {
      hapticFeedback('error')
      alert(error.response?.data?.detail || 'Failed to join game')
    },
  })

  // WebSocket connection
  const { isConnected, connectionStatus, lastMessage } = useBingoWebSocket(
    game?.status === 'PLAYING' || game?.status === 'PAUSED' ? gameId : null
  )

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return

    switch (lastMessage.event) {
      case 'NUMBER_CALLED':
        setCurrentNumber(lastMessage.data.number)
        setCalledNumbers((prev) => [...prev, lastMessage.data.number])
        hapticFeedback('light')
        break

      case 'WINNER_DECLARED':
        setWinnerData(lastMessage.data)
        setShowWinnerModal(true)
        hapticFeedback('heavy')
        break

      case 'GAME_FINISHED':
        setWinnerData(lastMessage.data)
        setShowWinnerModal(true)
        break

      case 'GAME_STATE':
        // Sync state on reconnection
        if (lastMessage.data.current_number) {
          setCurrentNumber(lastMessage.data.current_number)
        }
        if (lastMessage.data.called_numbers) {
          setCalledNumbers(lastMessage.data.called_numbers)
        }
        break
    }
  }, [lastMessage])

  if (!isAuthenticated || !user) {
    return <LoadingPage text="Authenticating..." />
  }

  if (gameLoading) {
    return <LoadingPage text="Loading game..." />
  }

  if (!game) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-xl mb-4">Game not found</p>
            <Link href="/games">
              <Button>Back to Games</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  // If game is waiting and user hasn't joined
  if (game.status === 'WAITING' && !cartela && !cartelaLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
        <div className="max-w-2xl mx-auto">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center mb-6">
                <h1 className="text-3xl font-bold mb-2">Game #{game.game_number}</h1>
                <GameStatus
                  status={game.status}
                  prizePool={game.prize_pool}
                  className="mb-4"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6 text-center">
                <div>
                  <p className="text-sm text-muted-foreground">Entry Fee</p>
                  <p className="text-2xl font-bold">{game.entry_fee} ETB</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Prize Pool</p>
                  <p className="text-2xl font-bold text-green-600">{game.prize_pool} ETB</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Max Players</p>
                  <p className="text-xl font-bold">{game.max_players}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Min to Start</p>
                  <p className="text-xl font-bold">{game.min_players}</p>
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 mb-6">
                <h3 className="font-semibold mb-2">🎮 How to Play:</h3>
                <ul className="text-sm space-y-1 text-muted-foreground">
                  <li>• Complete any row, column, diagonal, or full card</li>
                  <li>• First to win gets 100% of the prize pool</li>
                  <li>• Numbers are called every 5 seconds</li>
                  <li>• Game lasts maximum 5 minutes</li>
                </ul>
              </div>

              <Button
                variant="primary"
                size="lg"
                className="w-full"
                onClick={() => joinMutation.mutate()}
                disabled={joinMutation.isPending || user.play_wallet < game.entry_fee}
                isLoading={joinMutation.isPending}
              >
                {user.play_wallet < game.entry_fee
                  ? 'Insufficient Balance'
                  : `Join Game (${game.entry_fee} ETB)`}
              </Button>

              {user.play_wallet < game.entry_fee && (
                <p className="text-sm text-red-600 text-center mt-2">
                  You need {(game.entry_fee - user.play_wallet).toFixed(2)} ETB more to join
                </p>
              )}

              <Link href="/games">
                <Button variant="outline" className="w-full mt-3">
                  Back to Games
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Main game screen
  const calledNumbersSet = new Set(calledNumbers)

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800 pb-20">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-4 sticky top-0 z-10 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold">Game #{game.game_number}</h1>
            <ConnectionStatus status={connectionStatus} />
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 space-y-4">
        {/* Game Status */}
        <GameStatus status={game.status} prizePool={game.prize_pool} />

        {/* Current Number */}
        {game.status === 'PLAYING' && <CurrentNumber number={currentNumber} />}

        {/* Bingo Card */}
        {cartela ? (
          <BingoCard numbers={cartela.numbers} calledNumbers={calledNumbersSet} />
        ) : cartelaLoading ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">Loading your bingo card...</p>
          </div>
        ) : (
          <Card>
            <CardContent className="pt-6 text-center">
              <p className="text-muted-foreground">
                {game.status === 'WAITING'
                  ? 'Join the game to get your card'
                  : 'You are not in this game'}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Called Numbers */}
        {calledNumbers.length > 0 && <CalledNumbers numbers={calledNumbers} />}

        {/* Game Info */}
        {game.status === 'WAITING' && (
          <Card>
            <CardContent className="pt-6 text-center">
              <p className="text-lg font-semibold mb-2">⏳ Waiting for players...</p>
              <p className="text-sm text-muted-foreground">
                Game will start when {game.min_players} or more players join
              </p>
            </CardContent>
          </Card>
        )}

        {game.status === 'FINISHED' && (
          <Card>
            <CardContent className="pt-6 text-center">
              <p className="text-lg font-semibold mb-4">🏁 Game Finished</p>
              <Link href="/games">
                <Button variant="primary" className="w-full">
                  Back to Games
                </Button>
              </Link>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Winner Modal */}
      <WinnerModal
        isOpen={showWinnerModal}
        isWinner={winnerData?.winner?.user_id === user.id}
        winnerName={winnerData?.winner?.username}
        prizeAmount={winnerData?.winner?.prize_amount}
        winningPattern={winnerData?.winner?.winning_pattern}
        onClose={() => {
          setShowWinnerModal(false)
          if (game.status === 'FINISHED') {
            router.push('/games')
          }
        }}
      />
    </div>
  )
}
