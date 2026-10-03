'use client'

import { useEffect, useState } from 'react'
import { adminApi } from '@/lib/api/endpoints'
import { AdminStats } from '@/lib/api/types'
import { Card } from '@/components/ui/Card'
import { Loading } from '@/components/ui/Loading'

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadStats()
    const interval = setInterval(loadStats, 30000) // Refresh every 30s
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const data = await adminApi.getStats()
      setStats(data)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <Loading type="page" />
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
        {error}
      </div>
    )
  }

  if (!stats) {
    return null
  }

  const statCards = [
    {
      title: 'Total Users',
      value: stats.total_users,
      subtitle: `${stats.registered_users} registered`,
      icon: '👥',
      color: 'blue',
    },
    {
      title: 'Total Games',
      value: stats.total_games,
      subtitle: `${stats.active_games} active`,
      icon: '🎮',
      color: 'green',
    },
    {
      title: 'Finished Games',
      value: stats.finished_games,
      subtitle: 'Completed',
      icon: '🏁',
      color: 'purple',
    },
    {
      title: 'Total Deposits',
      value: `${stats.total_deposits.toLocaleString()} ETB`,
      subtitle: 'All time',
      icon: '💰',
      color: 'emerald',
    },
    {
      title: 'Total Withdrawals',
      value: `${stats.total_withdrawals.toLocaleString()} ETB`,
      subtitle: 'All time',
      icon: '💸',
      color: 'red',
    },
    {
      title: 'Pending Withdrawals',
      value: stats.pending_withdrawals,
      subtitle: 'Requires approval',
      icon: '⏳',
      color: 'orange',
    },
    {
      title: 'Total Transfers',
      value: `${stats.total_transfers.toLocaleString()} ETB`,
      subtitle: 'All time',
      icon: '🔄',
      color: 'indigo',
    },
    {
      title: 'Pending Transfers',
      value: stats.pending_transfers,
      subtitle: 'Requires approval',
      icon: '⏳',
      color: 'yellow',
    },
  ]

  const colorMap: Record<string, string> = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    red: 'bg-red-50 text-red-600',
    orange: 'bg-orange-50 text-orange-600',
    indigo: 'bg-indigo-50 text-indigo-600',
    yellow: 'bg-yellow-50 text-yellow-600',
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Platform statistics and overview</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, index) => (
          <Card key={index} className="hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</p>
                <p className="text-xs text-gray-500">{stat.subtitle}</p>
              </div>
              <div className={`p-3 rounded-lg ${colorMap[stat.color]}`}>
                <span className="text-2xl">{stat.icon}</span>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold">Quick Actions</h2>
          </Card.Header>
          <Card.Content>
            <div className="space-y-3">
              <a
                href="/admin/games"
                className="block px-4 py-3 bg-blue-50 hover:bg-blue-100 rounded-lg text-blue-700 font-medium transition-colors"
              >
                🎮 Manage Games
              </a>
              <a
                href="/admin/withdrawals"
                className="block px-4 py-3 bg-orange-50 hover:bg-orange-100 rounded-lg text-orange-700 font-medium transition-colors"
              >
                💸 Review Withdrawals ({stats.pending_withdrawals})
              </a>
              <a
                href="/admin/transfers"
                className="block px-4 py-3 bg-yellow-50 hover:bg-yellow-100 rounded-lg text-yellow-700 font-medium transition-colors"
              >
                🔄 Review Transfers ({stats.pending_transfers})
              </a>
              <a
                href="/admin/users"
                className="block px-4 py-3 bg-purple-50 hover:bg-purple-100 rounded-lg text-purple-700 font-medium transition-colors"
              >
                👥 Manage Users
              </a>
            </div>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <h2 className="text-lg font-semibold">System Status</h2>
          </Card.Header>
          <Card.Content>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Backend API</span>
                <span className="flex items-center text-green-600">
                  <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                  Online
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Database</span>
                <span className="flex items-center text-green-600">
                  <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                  Connected
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Redis</span>
                <span className="flex items-center text-green-600">
                  <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                  Connected
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">WebSocket</span>
                <span className="flex items-center text-green-600">
                  <span className="w-2 h-2 bg-green-600 rounded-full mr-2"></span>
                  Active
                </span>
              </div>
            </div>
          </Card.Content>
        </Card>
      </div>
    </div>
  )
}
