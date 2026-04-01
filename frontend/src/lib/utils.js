import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatNumber(num) {
  return new Intl.NumberFormat('en-US').format(num)
}

export function formatCurrency(num) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(num)
}

export function formatPercent(num, decimals = 1) {
  return `${num.toFixed(decimals)}%`
}

export function formatDate(dateString) {
  if (!dateString) return '—'
  // Backend stores UTC without 'Z' suffix — append it so JS converts to local time correctly
  const utcString = dateString.endsWith('Z') || dateString.includes('+') ? dateString : dateString + 'Z'
  return new Date(utcString).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function getStatusColor(status) {
  switch (status) {
    case 'healthy':
    case 'completed':
    case 'success':
      return 'text-green-600 bg-green-50'
    case 'watch':
    case 'running':
    case 'pending':
      return 'text-yellow-600 bg-yellow-50'
    case 'at_risk':
    case 'warning':
      return 'text-orange-600 bg-orange-50'
    case 'critical':
    case 'failed':
    case 'error':
      return 'text-red-600 bg-red-50'
    default:
      return 'text-gray-600 bg-gray-50'
  }
}

export function getSeverityColor(severity) {
  switch (severity) {
    case 'critical':
      return 'text-red-600'
    case 'high':
      return 'text-orange-600'
    case 'medium':
      return 'text-yellow-600'
    case 'low':
      return 'text-blue-600'
    default:
      return 'text-gray-600'
  }
}
