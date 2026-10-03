'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { adminApi } from '@/lib/api/endpoints'
import { BingoGame, GamePlayer } from '@/lib/api/types'
import { Card } from '@/components/ui/Card'
import { Loading } from '@/components/ui/Loading'
import { Button } from '@/components/ui/Button'

export default function AdminGameDetailPage() {
  const params = useParams()
  const router = useRouter()
  const gameId = Number(params.id)

  const [game, setGame] = useState<BingoGame | null>(null)
  const [players, setPlayers] = useState<GamePlayer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadGameData()
    const interval = setInterval(loadGameData, 5000) // Refresh every 5s
    return () => clearInterval(interval)
  }, [gameId])

  const loadGameData = async () => {
    try {
      const [gameData, playersData] = await Promise.all([
        adminApi.getGame(gameId),
        adminApi.getGamePlayers(gameId),
      ])
      setGame(gameData)
      setPlayers(playersData)
      setError('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load game data')
    } finally {
      setLoading(false)
    }
  }

  const handleStart = async () => {
    if (!confirm('Start this game now?')) return
    try {
      await adminApi.startGame(gameId)
      await loadGameData()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start game')
    }
  }

  const handlePause = async () => {
    try {
      await adminApi.pauseGame(gameId)
      await loadGameData()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to pause game')
    }
  }

  const handleResume = async () => {
    try {
      await adminApi.resumeGame(gameId)
      await loadGameData()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to resume game')
    }
  }

  const handleCancel = async () => {
    if (!confirm('Cancel this game? All players will be refunded.')) return
    try {
      await adminApi.cancelGame(gameId)
      await loadGameData()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to cancel game')
    }
  }

  if (loading) {
    return <Loading type="page" />
  }

  if (error || !game) {
    return (
      <div>
        <button onClick={() => router.back()} className="mb-4 text-blue-600 hover:text-blue-800">
          ← Back
        </button>
        <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-lg">
          {error || 'Game not found'}
        </div>
      </div>
    )
  }

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      WAITING: 'bg-yellow-100 text-yellow-800',
      PLAYING: 'bg-green-100 text-green-800',
      PAUSED: 'bg-orange-100 text-orange-800',
      FINISHED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div>
      <button onClick={() => router.back()} className="mb-4 text-blue-600 hover:text-blue-800">
        ← Back to Games
      </button>

      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Game #{game.game_number}
        </h1>
        <span className={`inline-block px-3 py-1 text-sm font-medium rounded-full ${getStatusColor(game.status)}`}>
          {game.status}
        </span>
      </div>

      {/* Game Controls */}
      <Card className="mb-6">
        <Card.Header>
          <h2 className="text-lg font-semibold">Game Controls</h2>
        </Card.Header>
        <Card.Content>
          <div className="flex flex-wrap gap-3">
            {game.status === 'WAITING' && (
              <>
                <Button onClick={handleStart} variant="primary">
                  ▶️ Start Game
                </Button>
                <Button onClick={handleCancel} variant="danger">
                  ❌ Cancel Game
                </Button>
              </>
            )}
            {game.status === 'PLAYING' && (
              <>
                <Button onClick={handlePause} variant="secondary">
                  ⏸️ Pause Game
                </Button>
                <Button onClick={handleCancel} variant="danger">
                  ❌ Cancel Game
                </Button>
              </>
            )}
            {game.status === 'PAUSED' && (
              <>
                <Button onClick={handleResume} variant="primary">
                  ▶️ Resume Game
                </Button>
                <Button onClick={handleCancel} variant="danger">
                  ❌ Cancel Game
                </Button>
              </>
            )}
          </div>
        </Card.Content>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <Card>
          <Card.Header>
            <h3 className="text-sm font-medium text-gray-600">Entry Fee</h3>
          </Card.Header>
          <Card.Content>
            <p className="text-2xl font-bold text-gray-900">{game.entry_fee} ETB</p>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <h3 className="text-sm font-medium text-gray-600">Prize Pool</h3>
          </Card.Header>
          <Card.Content>
            <p className="text-2xl font-bold text-green-600">{game.prize_pool.toLocaleString()} ETB</p>
          </Card.Content>
        </Card>

        <Card>
          <Card.Header>
            <h3 className="text-sm font-medium text-gray-600">Players</h3>
          </Card.Header>
          <Card.Content>
            <p className="text-2xl font-bold text-blue-600">
              {players.length} / {game.max_players}
            </p>
            <p className="text-sm text-gray-500">Min: {game.min_players}</p>
          </Card.Content>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <Card.Header>
            <h3 className="text-sm font-medium text-gray-600">Created</h3>
          </Card.Header>
          <Card.Content>
            <p className="text-gray-900">{new Date(game.created_at).toLocaleString()}</p>
          </Card.Content>
        </Card>

        {game.started_at && (
          <Card>
            <Card.Header>
              <h3 className="text-sm font-medium text-gray-600">Started</h3>
            </Card.Header>
            <Card.Content>
              <p className="text-gray-900">{new Date(game.started_at).toLocaleString()}</p>
            </Card.Content>
          </Card>
        )}

        {game.finished_at && (
          <Card>
            <Card.Header>
              <h3 className="text-sm font-medium text-gray-600">Finished</h3>
            </Card.Header>
            <Card.Content>
              <p className="text-gray-900">{new Date(game.finished_at).toLocaleString()}</p>
            </Card.Content>
          </Card>
        )}
      </div>

      {/* Players List */}
      <Card>
        <Card.Header>
          <h2 className="text-lg font-semibold">Players ({players.length})</h2>
        </Card.Header>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Player ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Entry Fee
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Winner
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Prize
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Joined
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {players.map((player) => (
                <tr key={player.id} className={player.is_winner ? 'bg-green-50' : 'hover:bg-gray-50'}>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    User #{player.user_id}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{player.status}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{player.entry_fee} ETB</td>
                  <td className="px-6 py-4">
                    {player.is_winner ? (
                      <span className="text-green-600 font-medium">🏆 Winner</span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-green-600">
                    {player.prize_amount > 0 ? `${player.prize_amount.toLocaleString()} ETB` : '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(player.joined_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
