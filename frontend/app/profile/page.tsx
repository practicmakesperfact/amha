'use client'

import { useQuery } from '@tanstack/react-query'
import { playerApi } from '@/lib/api/endpoints'
import { useAuth } from '@/providers/auth-provider'
import { useTelegram } from '@/hooks/useTelegram'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { LoadingPage } from '@/components/ui/Loading'
import { formatPhoneNumber } from '@/lib/utils/format'
import Link from 'next/link'

export default function ProfilePage() {
  const { user, isAuthenticated, logout } = useAuth()
  const { webApp } = useTelegram()

  const { data: stats } = useQuery({
    queryKey: ['my-stats'],
    queryFn: () => playerApi.getMyStats(),
    enabled: isAuthenticated,
  })

  if (!isAuthenticated || !user) {
    return <LoadingPage text="Please authenticate..." />
  }

  const handleLogout = () => {
    logout()
    if (webApp) {
      webApp.close()
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold">👤 My Profile</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 space-y-4">
        {/* User Info */}
        <Card>
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                {user.full_name.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="text-xl font-bold">{user.full_name}</p>
                <p className="text-sm text-muted-foreground">@{user.username}</p>
              </div>
            </div>

            <div className="space-y-3 pt-4 border-t">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Phone Number</span>
                <span className="font-medium">{formatPhoneNumber(user.phone_number)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Telegram ID</span>
                <span className="font-mono text-sm">{user.telegram_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Member Since</span>
                <span className="font-medium">
                  {new Date(user.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Registration Status</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 text-xs font-medium rounded">
                  {user.is_registered ? '✓ Registered' : 'Not Registered'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Game Statistics */}
        {stats && (
          <Card>
            <CardHeader>
              <CardTitle>Game Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-center">
                  <p className="text-3xl font-bold text-blue-600">{stats.games_played}</p>
                  <p className="text-sm text-muted-foreground">Games Played</p>
                </div>
                <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg text-center">
                  <p className="text-3xl font-bold text-green-600">{stats.games_won}</p>
                  <p className="text-sm text-muted-foreground">Games Won</p>
                </div>
                <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg text-center">
                  <p className="text-3xl font-bold text-purple-600">{stats.win_rate.toFixed(1)}%</p>
                  <p className="text-sm text-muted-foreground">Win Rate</p>
                </div>
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg text-center">
                  <p className="text-3xl font-bold text-yellow-600">
                    {stats.total_winnings.toFixed(0)}
                  </p>
                  <p className="text-sm text-muted-foreground">Total Winnings (ETB)</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Achievements */}
        <Card>
          <CardHeader>
            <CardTitle>Achievements</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 border rounded-lg text-center">
                <span className="text-3xl">🏆</span>
                <p className="text-sm font-medium mt-1">{user.wins} Wins</p>
              </div>
              <div className="p-3 border rounded-lg text-center">
                <span className="text-3xl">🪙</span>
                <p className="text-sm font-medium mt-1">{user.coin} Coins</p>
              </div>
              {stats && stats.games_played >= 10 && (
                <div className="p-3 border rounded-lg text-center bg-gradient-to-br from-yellow-50 to-yellow-100">
                  <span className="text-3xl">⭐</span>
                  <p className="text-sm font-medium mt-1">Regular Player</p>
                </div>
              )}
              {stats && stats.games_won >= 5 && (
                <div className="p-3 border rounded-lg text-center bg-gradient-to-br from-purple-50 to-purple-100">
                  <span className="text-3xl">👑</span>
                  <p className="text-sm font-medium mt-1">Champion</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Links */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Links</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link href="/games">
              <Button variant="outline" className="w-full justify-start">
                🎮 Play Bingo
              </Button>
            </Link>
            <Link href="/wallet">
              <Button variant="outline" className="w-full justify-start">
                💰 My Wallet
              </Button>
            </Link>
            <Link href="/history">
              <Button variant="outline" className="w-full justify-start">
                📜 Game History
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* App Info */}
        <Card>
          <CardHeader>
            <CardTitle>About</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-2">
            <p>
              <strong>AMHABINGO</strong> - Real-time Bingo game on Telegram
            </p>
            <p>Version 1.0.0</p>
            <p>© 2024 AMHABINGO. All rights reserved.</p>
          </CardContent>
        </Card>

        {/* Logout */}
        <Button variant="destructive" className="w-full" onClick={handleLogout}>
          🚪 Logout
        </Button>
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
          <Link href="/history" className="flex flex-col items-center p-2 text-muted-foreground hover:text-primary">
            <span className="text-xl">📜</span>
            <span className="text-xs">History</span>
          </Link>
          <Link href="/profile" className="flex flex-col items-center p-2 text-primary">
            <span className="text-xl">👤</span>
            <span className="text-xs">Profile</span>
          </Link>
        </div>
      </nav>
    </div>
  )
}
