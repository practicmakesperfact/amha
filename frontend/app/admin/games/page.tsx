'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { adminApi } from '@/lib/api/endpoints'
import { BingoGame } from '@/lib/api/types'
import { Card } from '@/components/ui/Card'
import { Loading } from '@/components/ui/Loading'
import { Button } from '@/components/ui/Button'

export default function AdminGamesPage() {
  const [games, setGames] = useState<BingoGame[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [page, setPage] = useState(0)
  const [total, setTotal] = useState(0)
  const limit = 50

  const [createForm, setCreateForm] = useState({
    entry_fee: 10,
    max_players: 50,
    min_players: 2,
  })

  useEffect(() => {
    loadGames()
    const interval = setInterval(loadGames, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [page])

  const loadGames = async () => {
    setLoading(true)
    try {
      const data = await adminApi.getAdminGames(page * limit, limit)
      setGames(data.items)
      setTotal(data.total)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load games')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateGame = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    try {
      await adminApi.createGame(createForm)
      setShowCreateModal(false)
      setCreateForm({ entry_fee: 10, max_players: 50, min_players: 2 })
      await loadGames()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create game')
    } finally {
      setCreating(false)
    }
  }

  const handleStartGame = async (gameId: number) => {
    if (!confirm('Start this game now?')) return
    try {
      await adminApi.startGame(gameId)
      await loadGames()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start game')
    }
  }

  const handleCancelGame = async (gameId: number) => {
    if (!confirm('Cancel this game? All players will be refunded.')) return
    try {
      await adminApi.cancelGame(gameId)
      await loadGames()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel game')
    }
  }

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      WAITING: 'bg-yellow-100 text-yellow-800',
      PLAYING: 'bg-green-100 text-green-800',
      PAUSED: 'bg-orange-100 text-orange-800',
      FINISHED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Games</h1>
          <p className="text-gray-600">Manage bingo games</p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          🎮 Create Game
        </Button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <Loading type="page" />
      ) : (
        <>
          <Card>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Game #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Entry Fee
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Players
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Prize Pool
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Created
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {games.map((game) => (
                    <tr key={game.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <Link
                          href={`/admin/games/${game.id}`}
                          className="font-medium text-blue-600 hover:text-blue-800"
                        >
                          #{game.game_number}
                        </Link>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusBadge(game.status)}`}>
                          {game.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {game.entry_fee} ETB
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {game.min_players} - {game.max_players}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">
                        {game.prize_pool.toLocaleString()} ETB
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(game.created_at).toLocaleString()}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex space-x-2">
                          {game.status === 'WAITING' && (
                            <button
                              onClick={() => handleStartGame(game.id)}
                              className="text-sm text-green-600 hover:text-green-800"
                            >
                              Start
                            </button>
                          )}
                          {(game.status === 'WAITING' || game.status === 'PLAYING') && (
                            <button
                              onClick={() => handleCancelGame(game.id)}
                              className="text-sm text-red-600 hover:text-red-800"
                            >
                              Cancel
                            </button>
                          )}
                          <Link
                            href={`/admin/games/${game.id}`}
                            className="text-sm text-blue-600 hover:text-blue-800"
                          >
                            View
                          </Link>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Showing {page * limit + 1} to {Math.min((page + 1) * limit, total)} of {total} games
              </p>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                  disabled={page >= totalPages - 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Create Game Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold mb-4">Create New Game</h2>
            <form onSubmit={handleCreateGame} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Entry Fee (ETB)
                </label>
                <input
                  type="number"
                  value={createForm.entry_fee}
                  onChange={(e) => setCreateForm({ ...createForm, entry_fee: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  min="1"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Maximum Players
                </label>
                <input
                  type="number"
                  value={createForm.max_players}
                  onChange={(e) => setCreateForm({ ...createForm, max_players: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  min="2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Players
                </label>
                <input
                  type="number"
                  value={createForm.min_players}
                  onChange={(e) => setCreateForm({ ...createForm, min_players: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                  min="2"
                  max={createForm.max_players}
                  required
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={creating} className="flex-1">
                  {creating ? 'Creating...' : 'Create'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
