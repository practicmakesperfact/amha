'use client'

import { useAuth } from '@/providers/auth-provider'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { formatCurrency, formatDateTime } from '@/lib/utils/format'
import Link from 'next/link'
import { LoadingPage } from '@/components/ui/Loading'

export default function WalletPage() {
  const { user, isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <LoadingPage text="Loading wallet..." />
  }

  if (!isAuthenticated || !user) {
    return <LoadingPage text="Please authenticate..." />
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pb-24">
      {/* Header */}
      <div className="bg-primary text-primary-foreground p-4">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold">💰 My Wallet</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 space-y-4">
        {/* Wallet Balances */}
        <Card>
          <CardHeader>
            <CardTitle>Wallet Balances</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Main Wallet</p>
                <p className="text-3xl font-bold text-green-600">
                  {formatCurrency(user.main_wallet)}
                </p>
                <p className="text-xs text-muted-foreground mt-2">For deposits & withdrawals</p>
              </div>
              <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Play Wallet</p>
                <p className="text-3xl font-bold text-blue-600">
                  {formatCurrency(user.play_wallet)}
                </p>
                <p className="text-xs text-muted-foreground mt-2">For joining games</p>
              </div>
              <div className="p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Coins</p>
                <p className="text-3xl font-bold text-yellow-600">🪙 {user.coin}</p>
                <p className="text-xs text-muted-foreground mt-2">Bonus rewards</p>
              </div>
              <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg">
                <p className="text-sm text-muted-foreground mb-1">Wins</p>
                <p className="text-3xl font-bold text-purple-600">🏆 {user.wins}</p>
                <p className="text-xs text-muted-foreground mt-2">Total victories</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Wallet Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
              <p className="text-sm mb-3">
                💡 <strong>Note:</strong> For deposits, withdrawals, and transfers, please use the Telegram bot.
              </p>
              <p className="text-xs text-muted-foreground">
                Open the bot and use the buttons: 💰 Deposit, 💸 Withdraw, 🎁 Transfer
              </p>
            </div>

            <Button variant="outline" className="w-full" disabled>
              💰 Deposit (Use Telegram Bot)
            </Button>
            <Button variant="outline" className="w-full" disabled>
              💸 Withdraw (Use Telegram Bot)
            </Button>
            <Button variant="outline" className="w-full" disabled>
              🎁 Transfer (Use Telegram Bot)
            </Button>
          </CardContent>
        </Card>

        {/* Transaction History Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-center text-muted-foreground py-8">
              Transaction history coming soon...
            </p>
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
          <Link href="/wallet" className="flex flex-col items-center p-2 text-primary">
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
