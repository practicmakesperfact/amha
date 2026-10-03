'use client'

import { useAuth } from '@/providers/auth-provider'
import { useTelegram } from '@/hooks/useTelegram'
import { LoadingPage } from '@/components/ui/Loading'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { formatCurrency } from '@/lib/utils/format'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { playerApi } from '@/lib/api/endpoints'

export default function HomePage() {
  const { user, isLoading, isAuthenticated } = useAuth()
  const { isReady } = useTelegram()

  // Fetch available games
  const { data: gamesData, isLoading: gamesLoading } = useQuery({
    queryKey: ['games', 'available'],
    queryFn: () => playerApi.getGames(0, 5),
    enabled: isAuthenticated,
  })

  if (!isReady || isLoading) {
    return <LoadingPage text="Loading AMHABINGO..." />
  }

  if (!isAuthenticated || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">Welcome to AMHABINGO</CardTitle>
          </CardHeader>
          <CardContent className="text-center">
            <p className="text-muted-foreground mb-4">
              Please authenticate to start playing
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const games = gamesData?.items || []

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">🎮 AMHABINGO</h1>
          <p className="text-sm opacity-90">Welcome, {user.full_name}</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 space-y-6">
        {/* Wallet Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">💰 Your Wallet</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Main Wallet</p>
                <p className="text-2xl font-bold text-green-600">
                  {formatCurrency(user.main_wallet)}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Play Wallet</p>
                <p className="text-2xl font-bold text-blue-600">
                  {formatCurrency(user.play_wallet)}
                </p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Coins</p>
                <p className="text-xl font-bold text-yellow-600">🪙 {user.coin}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground">Wins</p>
                <p className="text-xl font-bold text-purple-600">🏆 {user.wins}</p>
              </div>
            </div>
            <div className="mt-4">
              <Link href="/wallet">
                <Button variant="outline" className="w-full">
                  Manage Wallet
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-2 gap-4">
          <Link href="/games">
            <Button variant="primary" size="lg" className="w-full h-24 flex flex-col gap-2">
              <span className="text-3xl">🎲</span>
              <span>Play Bingo</span>
            </Button>
          </Link>
          <Link href="/history">
            <Button variant="secondary" size="lg" className="w-full h-24 flex flex-col gap-2">
              <span className="text-3xl">📜</span>
              <span>History</span>
            </Button>
          </Link>
        </div>

        {/* Available Games */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-xl">🎯 Available Games</CardTitle>
              <Link href="/games">
                <Button variant="ghost" size="sm">
                  View All
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            {gamesLoading ? (
              <p className="text-center text-muted-foreground py-8">Loading games...</p>
            ) : games.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground mb-4">No active games right now</p>
                <p className="text-sm text-muted-foreground">
                  Check back later or contact support to create a game
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {games.map((game) => (
                  <div
                    key={game.id}
                    className="border rounded-lg p-4 hover:border-primary transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold">Game #{game.game_number}</p>
                        <p className="text-sm text-muted-foreground">
                          Entry: {formatCurrency(game.entry_fee)}
                        </p>
                        <p className="text-sm text-green-600 font-medium">
                          Prize: {formatCurrency(game.prize_pool)}
                        </p>
                      </div>
                      <Link href={`/games/${game.id}`}>
                        <Button size="sm">Join</Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Profile Link */}
        <Link href="/profile">
          <Button variant="outline" className="w-full">
            👤 View Profile & Stats
          </Button>
        </Link>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-background border-t p-2">
        <div className="max-w-4xl mx-auto flex justify-around">
          <Link href="/" className="flex flex-col items-center p-2 text-primary">
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

      {/* Spacer for bottom nav */}
      <div className="h-20" />
    </div>
  )
}
