'use client'

import { useQuery } from '@tanstack/react-query'
import { playerApi } from '@/lib/api/endpoints'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Loading } from '@/components/ui/Loading'
import { formatCurrency, formatDateTime } from '@/lib/utils/format'
import Link from 'next/link'
import { useAuth } from '@/providers/auth-provider'
import { useRouter } from 'next/navigation'
import { useTelegram } from '@/hooks/useTelegram'

export default function GamesPage() {
  const { user, isAuthenticated } = useAuth()
  const { hapticFeedback } = useTelegram()
  const router = useRouter()

  const { data: gamesData, isLoading, refetch } = useQuery({
    queryKey: ['games'],
    queryFn: () => playerApi.getGames(0, 50),
    enabled: isAuthenticated,
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  const games = gamesData?.items || []
  const waitingGames = games.filter((g) => g.status === 'WAITING')
  const playingGames = games.filter((g) => g.status === 'PLAYING')

  if (!isAuthenticated || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Please authenticate first</p>
      </div>
    )
  }

  const handleJoinGame = (gameId: number) => {
    hapticFeedback('medium')
    router.push(`/game/${gameId}`)
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-4 sticky top-0 z-10 shadow-lg">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">🎲 Bingo Games</h1>
            <p className="text-sm opacity-90">Join and win big!</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()} className="bg-white/20 border-white/30">
            🔄 Refresh
          </Button>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 space-y-6">
        {/* User Balance */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Play Wallet Balance</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(user.play_wallet)}
                </p>
              </div>
              <Link href="/wallet">
                <Button variant="outline" size="sm">
                  Add Funds
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loading size="lg" text="Loading games..." />
          </div>
        ) : (
          <>
            {/* Waiting Games */}
            {waitingGames.length > 0 && (
              <div>
                <h2 className="text-xl font-bold mb-3 flex items-center gap-2">
                  ⏳ Waiting to Start
                  <span className="text-sm font-normal text-muted-foreground">
                    ({waitingGames.length})
                  </span>
                </h2>
                <div className="space-y-3">
                  {waitingGames.map((game) => (
                    <Card key={game.id} className="hover:shadow-lg transition-shadow">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="text-lg font-bold">Game #{game.game_number}</h3>
                              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded">
                                WAITING
                              </span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <div>
                                <p className="text-muted-foreground">Entry Fee</p>
                                <p className="font-semibold">{formatCurrency(game.entry_fee)}</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Prize Pool</p>
                                <p className="font-semibold text-green-600">
                                  {formatCurrency(game.prize_pool)}
                                </p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Players</p>
                                <p className="font-semibold">
                                  ? / {game.max_players}
                                </p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Min to Start</p>
                                <p className="font-semibold">{game.min_players}</p>
                              </div>
                            </div>
                            <p className="text-xs text-muted-foreground mt-2">
                              Created {formatDateTime(game.created_at)}
                            </p>
                          </div>
                          <Button
                            variant="primary"
                            size="lg"
                            className="ml-4"
                            onClick={() => handleJoinGame(game.id)}
                            disabled={user.play_wallet < game.entry_fee}
                          >
                            Join
                          </Button>
                        </div>
                        {user.play_wallet < game.entry_fee && (
                          <p className="text-sm text-red-600 mt-2">
                            Insufficient balance. Add funds to join.
                          </p>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Playing Games */}
            {playingGames.length > 0 && (
              <div>
                <h2 className="text-xl font-bold mb-3 flex items-center gap-2">
                  🎮 In Progress
                  <span className="text-sm font-normal text-muted-foreground">
                    ({playingGames.length})
                  </span>
                </h2>
                <div className="space-y-3">
                  {playingGames.map((game) => (
                    <Card key={game.id} className="border-green-200 dark:border-green-800">
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="text-lg font-bold">Game #{game.game_number}</h3>
                              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                                LIVE
                              </span>
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <div>
                                <p className="text-muted-foreground">Prize Pool</p>
                                <p className="font-semibold text-green-600">
                                  {formatCurrency(game.prize_pool)}
                                </p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Started</p>
                                <p className="font-semibold">
                                  {game.started_at && formatDateTime(game.started_at)}
                                </p>
                              </div>
                            </div>
                          </div>
                          <Link href={`/game/${game.id}`}>
                            <Button variant="outline" size="lg" className="ml-4">
                              Watch
                            </Button>
                          </Link>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* No Games */}
            {games.length === 0 && (
              <Card>
                <CardContent className="py-12 text-center">
                  <div className="text-6xl mb-4">🎲</div>
                  <h3 className="text-xl font-bold mb-2">No Active Games</h3>
                  <p className="text-muted-foreground mb-4">
                    There are no games available right now.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Check back later or contact support to create a game.
                  </p>
                  <Button onClick={() => refetch()} className="mt-4">
                    Refresh Games
                  </Button>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-background border-t p-2">
        <div className="max-w-4xl mx-auto flex justify-around">
          <Link href="/" className="flex flex-col items-center p-2 text-muted-foreground hover:text-primary">
            <span className="text-xl">🏠</span>
            <span className="text-xs">Home</span>
          </Link>
          <Link href="/games" className="flex flex-col items-center p-2 text-primary">
            <span className="text-xl">🎮</span>
            <span className="text-xs">Games</span>
          </Link>
          <Link href="/wallet" className="flex flex-col items-center p-2 text-muted-foreground hover:text-primary">
            <span className="text-xl">💰</span>
            <span className="text-xs">Wallet</span>
          </Link>
          <Link href="/history" className="flex flex-col items-center p-2 text-muted-foreground hover:text-primary">
            <span className="text-xl">📜</span>
            <span className="text-xs">History</span>
          </Link>
          <Link href="/profile" className="flex flex-col items-center p-2 text-muted-foreground hover:text-primary">
            <span className="text-xl">👤</span>
            <span className="text-xs">Profile</span>
          </Link>
        </div>
      </nav>
    </div>
  )
}
