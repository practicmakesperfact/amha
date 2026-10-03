// Format currency in Ethiopian Birr
export function formatCurrency(amount: number): string {
  return `${amount.toFixed(2)} ETB`
}

// Format large numbers with commas
export function formatNumber(num: number): string {
  return num.toLocaleString()
}

// Format date to readable string
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

// Format date and time
export function formatDateTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Format relative time (e.g., "2 minutes ago")
export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) return 'just now'
  if (diffMin < 60) return `${diffMin} minute${diffMin > 1 ? 's' : ''} ago`
  if (diffHour < 24) return `${diffHour} hour${diffHour > 1 ? 's' : ''} ago`
  if (diffDay < 7) return `${diffDay} day${diffDay > 1 ? 's' : ''} ago`
  return formatDate(d)
}

// Get column letter for bingo number
export function getColumnLetter(number: number): 'B' | 'I' | 'N' | 'G' | 'O' {
  if (number >= 1 && number <= 15) return 'B'
  if (number >= 16 && number <= 30) return 'I'
  if (number >= 31 && number <= 45) return 'N'
  if (number >= 46 && number <= 60) return 'G'
  return 'O'
}

// Format phone number
export function formatPhoneNumber(phone: string): string {
  // Format Ethiopian phone numbers
  if (phone.startsWith('09') && phone.length === 10) {
    return `${phone.slice(0, 4)} ${phone.slice(4, 7)} ${phone.slice(7)}`
  }
  return phone
}

// Truncate text with ellipsis
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength - 3) + '...'
}
