'use client'

import { useQuery } from '@tanstack/react-query'
import { playerApi } from '@/lib/api/endpoints'
import { useAuth } from '@/providers/auth-provider'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Loading, LoadingPage } from '@/components/ui/Loading'
import { formatCurrency, formatDateTime } from '@/lib/utils/format'
import Link from 'next/link'

export default function HistoryPage() {
  const { user, isAuthenticated } = useAuth()

  const { data: gamesData, isLoading } = useQuery({
    queryKey: ['my-games'],
    queryFn: () => playerApi.getMyGames(0, 50),
    enabled: isAuthenticated,
  })

  const { data: stats } = useQuery({
    queryKey: ['my-stats'],
    queryFn: () => playerApi.getMyStats(),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated || !user) {
    return <LoadingPage text="Please authenticate..." />
  }

  const games = gamesData?.items || []

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold">📜 Game History</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 space-y-4">
        {/* Stats Summary */}
        {stats && (
          <Card>
            <CardHeader>
              <CardTitle>Your Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-sm text-muted-foreground">Games Played</p>
                  <p className="text-2xl font-bold">{stats.games_played}</p>
                </div>
                <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <p className="text-sm text-muted-foreground">Games Won</p>
                  <p className="text-2xl font-bold text-green-600">{stats.games_won}</p>
                </div>
                <div className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                  <p className="text-sm text-muted-foreground">Win Rate</p>
                  <p className="text-2xl font-bold">{stats.win_rate.toFixed(1)}%</p>
                </div>
                <div className="text-center p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <p className="text-sm text-muted-foreground">Entry Fees</p>
                  <p className="text-xl font-bold">{formatCurrency(stats.total_entry_fees)}</p>
                </div>
                <div className="text-center p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <p className="text-sm text-muted-foreground">Winnings</p>
                  <p className="text-xl font-bold text-green-600">
                    {formatCurrency(stats.total_winnings)}
                  </p>
                </div>
                <div className="text-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <p className="text-sm text-muted-foreground">Net Profit</p>
                  <p
                    className={`text-xl font-bold ${
                      stats.net_profit >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {formatCurrency(stats.net_profit)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Game History */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Games</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center py-8">
                <Loading text="Loading history..." />
              </div>
            ) : games.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-6xl mb-4">🎲</p>
                <p className="text-lg font-semibold mb-2">No games played yet</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Join your first game to see your history here
                </p>
                <Link href="/games">
                  <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium">
                    Browse Games
                  </button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {games.map((game) => (
                  <div
                    key={game.id}
                    className={`border rounded-lg p-4 ${
                      game.is_winner
                        ? 'border-green-300 bg-green-50 dark:border-green-800 dark:bg-green-900/20'
                        : 'border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">
                            {game.is_winner ? '🏆' : '🎲'}
                          </span>
                          <p className="font-semibold">
                            Game #{game.game_id}
                          </p>
                          {game.is_winner && (
                            <span className="px-2 py-1 bg-green-600 text-white text-xs font-medium rounded">
                              WON
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div>
                            <p className="text-muted-foreground">Entry Fee</p>
                            <p className="font-semibold">{formatCurrency(game.entry_fee)}</p>
                          </div>
                          {game.is_winner && (
                            <div>
                              <p className="text-muted-foreground">Prize Won</p>
                              <p className="font-semibold text-green-600">
                                {formatCurrency(game.prize_amount)}
                              </p>
                            </div>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-2">
                          {formatDateTime(game.joined_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-background border-t p-2">
        <div className="max-w-4xl mx-auto flex justify-around">
          <Link href="/" className="flex flex-col items-center p-2 text-muted-foreground hover:text-primary">
            <span className="text-xl">🏠</span>
            <span className="text-xs">Home</span>
          </Link>
          <Link href="/games" className="flex flex-col items-center p-2 text-muted-foreground hover:text-primary">
            <span className="text-xl">🎮</span>
            <span className="text-xs">Games</span>
          </Link>
          <Link href="/wallet" className="flex flex-col items-center p-2 text-muted-foreground hover:text-primary">
            <span className="text-xl">💰</span>
            <span className="text-xs">Wallet</span>
          </Link>
          <Link href="/history" className="flex flex-col items-center p-2 text-primary">
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
