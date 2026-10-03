import { apiClient } from './client'
import {
  BingoGame,
  Cartela,
  PlayerStats,
  PaginatedResponse,
  GamePlayer,
  CalledNumber,
  AdminStats,
  User,
  Deposit,
  Withdrawal,
  Transfer,
  WalletTransaction,
} from './types'

// ============================================
// PLAYER ENDPOINTS
// ============================================

export const playerApi = {
  // Games
  getGames: async (skip = 0, limit = 20) => {
    const response = await apiClient.get<PaginatedResponse<BingoGame>>(
      `/api/v1/bingo/games?skip=${skip}&limit=${limit}`
    )
    return response.data
  },

  getGame: async (gameId: number) => {
    const response = await apiClient.get<BingoGame>(`/api/v1/bingo/games/${gameId}`)
    return response.data
  },

  joinGame: async (gameId: number) => {
    const response = await apiClient.post<{ player: GamePlayer; cartela: Cartela }>(
      `/api/v1/bingo/games/${gameId}/join`
    )
    return response.data
  },

  getGameState: async (gameId: number) => {
    const response = await apiClient.get(`/api/v1/bingo/games/${gameId}/state`)
    return response.data
  },

  getCartela: async (gameId: number) => {
    const response = await apiClient.get<Cartela>(`/api/v1/bingo/games/${gameId}/cartela`)
    return response.data
  },

  getMyGames: async (skip = 0, limit = 20) => {
    const response = await apiClient.get<PaginatedResponse<GamePlayer>>(
      `/api/v1/bingo/me/games?skip=${skip}&limit=${limit}`
    )
    return response.data
  },

  getMyStats: async () => {
    const response = await apiClient.get<PlayerStats>('/api/v1/bingo/me/stats')
    return response.data
  },
}

// ============================================
// AUTH ENDPOINTS
// ============================================

export const authApi = {
  login: async (initData: string, telegramUser: any) => {
    const response = await apiClient.post('/auth/telegram', {
      init_data: initData,
      telegram_user: telegramUser,
    })
    return response.data
  },

  getMe: async () => {
    const response = await apiClient.get<{ user: User }>('/auth/me')
    return response.data
  },
}

// ============================================
// WALLET ENDPOINTS
// ============================================

export const walletApi = {
  getBalance: async () => {
    const response = await apiClient.get('/wallet/balance')
    return response.data
  },

  getTransactions: async (skip = 0, limit = 50) => {
    const response = await apiClient.get<PaginatedResponse<WalletTransaction>>(
      `/wallet/transactions?skip=${skip}&limit=${limit}`
    )
    return response.data
  },
}

// ============================================
// ADMIN ENDPOINTS
// ============================================

export const adminApi = {
  // Stats
  getStats: async () => {
    const response = await apiClient.get<AdminStats>('/admin/stats')
    return response.data
  },

  // Users
  getUsers: async (skip = 0, limit = 50, search?: string) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (search) params.append('search', search)
    
    const response = await apiClient.get<PaginatedResponse<User>>(
      `/admin/users?${params.toString()}`
    )
    return response.data
  },

  getUser: async (userId: number) => {
    const response = await apiClient.get<User>(`/admin/users/${userId}`)
    return response.data
  },

  // Games
  getAdminGames: async (skip = 0, limit = 50) => {
    const response = await apiClient.get<PaginatedResponse<BingoGame>>(
      `/admin/games?skip=${skip}&limit=${limit}`
    )
    return response.data
  },

  getGame: async (gameId: number) => {
    const response = await apiClient.get<BingoGame>(`/admin/games/${gameId}`)
    return response.data
  },

  createGame: async (data: {
    entry_fee: number
    max_players: number
    min_players: number
  }) => {
    const response = await apiClient.post<BingoGame>('/admin/games', data)
    return response.data
  },

  startGame: async (gameId: number) => {
    const response = await apiClient.post(`/admin/games/${gameId}/start`)
    return response.data
  },

  pauseGame: async (gameId: number) => {
    const response = await apiClient.post(`/admin/games/${gameId}/pause`)
    return response.data
  },

  resumeGame: async (gameId: number) => {
    const response = await apiClient.post(`/admin/games/${gameId}/resume`)
    return response.data
  },

  cancelGame: async (gameId: number) => {
    const response = await apiClient.post(`/admin/games/${gameId}/cancel`)
    return response.data
  },

  getGamePlayers: async (gameId: number) => {
    const response = await apiClient.get<GamePlayer[]>(`/admin/games/${gameId}/players`)
    return response.data
  },

  getGameEvents: async (gameId: number) => {
    const response = await apiClient.get(`/admin/games/${gameId}/events`)
    return response.data
  },

  // Deposits
  getDeposits: async (skip = 0, limit = 50, status?: string) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (status) params.append('status', status)
    
    const response = await apiClient.get<PaginatedResponse<Deposit>>(
      `/admin/deposits?${params.toString()}`
    )
    return response.data
  },

  // Withdrawals
  getWithdrawals: async (skip = 0, limit = 50, status?: string) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (status) params.append('status', status)
    
    const response = await apiClient.get<PaginatedResponse<Withdrawal>>(
      `/admin/withdrawals?${params.toString()}`
    )
    return response.data
  },

  approveWithdrawal: async (withdrawalId: number) => {
    const response = await apiClient.post(`/admin/withdrawals/${withdrawalId}/approve`)
    return response.data
  },

  rejectWithdrawal: async (withdrawalId: number) => {
    const response = await apiClient.post(`/admin/withdrawals/${withdrawalId}/reject`)
    return response.data
  },

  // Transfers
  getTransfers: async (skip = 0, limit = 50, status?: string) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (status) params.append('status', status)
    
    const response = await apiClient.get<PaginatedResponse<Transfer>>(
      `/admin/transfers?${params.toString()}`
    )
    return response.data
  },

  approveTransfer: async (transferId: number) => {
    const response = await apiClient.post(`/admin/transfers/${transferId}/approve`)
    return response.data
  },

  rejectTransfer: async (transferId: number) => {
    const response = await apiClient.post(`/admin/transfers/${transferId}/reject`)
    return response.data
  },

  // Transactions
  getTransactions: async (skip = 0, limit = 50) => {
    const response = await apiClient.get<PaginatedResponse<WalletTransaction>>(
      `/admin/transactions?skip=${skip}&limit=${limit}`
    )
    return response.data
  },
}
