// User types
export interface User {
  id: number
  telegram_id: number
  username: string
  full_name: string
  phone_number: string
  main_wallet: number
  play_wallet: number
  coin: number
  wins: number
  is_registered: boolean
  created_at: string
}

// Bingo Game types
export interface BingoGame {
  id: number
  game_number: number
  status: 'WAITING' | 'PLAYING' | 'PAUSED' | 'FINISHED' | 'CANCELLED'
  entry_fee: number
  prize_pool: number
  max_players: number
  min_players: number
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface GamePlayer {
  id: number
  game_id: number
  user_id: number
  cartela_id: number
  entry_fee: number
  status: string
  is_winner: boolean
  prize_amount: number
  joined_at: string
}

export interface Cartela {
  id: number
  game_id: number
  user_id: number
  numbers: number[][] // 5x5 grid
  created_at: string
}

export interface CalledNumber {
  id: number
  game_id: number
  number: number
  sequence: number
  called_at: string
}

export interface GameEvent {
  id: number
  game_id: number
  event_type: string
  event_data: any
  created_at: string
}

// Wallet types
export interface WalletTransaction {
  id: number
  user_id: number
  transaction_type: string
  amount: number
  balance_before: number
  balance_after: number
  status: string
  reference_id: string
  description: string
  created_at: string
}

export interface Deposit {
  id: number
  user_id: number
  amount: number
  status: string
  reference: string
  created_at: string
}

export interface Withdrawal {
  id: number
  user_id: number
  amount: number
  telebirr_number: string
  status: string
  created_at: string
}

export interface Transfer {
  id: number
  sender_id: number
  receiver_id: number
  amount: number
  status: string
  created_at: string
}

// WebSocket event types
export interface WebSocketEvent {
  event: string
  game_id: number
  data: any
  timestamp: string
}

export interface NumberCalledEvent {
  event: 'NUMBER_CALLED'
  game_id: number
  number: number
  column: 'B' | 'I' | 'N' | 'G' | 'O'
  sequence: number
  timestamp: string
}

export interface WinnerDeclaredEvent {
  event: 'WINNER_DECLARED'
  game_id: number
  winner: {
    user_id: number
    username: string
    prize_amount: number
    winning_pattern: string
  }
  timestamp: string
}

export interface GameFinishedEvent {
  event: 'GAME_FINISHED'
  game_id: number
  winners: Array<{
    user_id: number
    username: string
    prize_amount: number
  }>
  timestamp: string
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

export interface PlayerStats {
  games_played: number
  games_won: number
  win_rate: number
  total_entry_fees: number
  total_winnings: number
  net_profit: number
}

// Admin types
export interface AdminStats {
  total_users: number
  registered_users: number
  total_games: number
  active_games: number
  finished_games: number
  total_deposits: number
  total_withdrawals: number
  total_transfers: number
  pending_withdrawals: number
  pending_transfers: number
}
