import { create } from 'zustand'

const initialNotifications = [
  {
    id: 'n1',
    title: 'MCH-002 Critical Risk',
    message: 'Bearing failure risk at 58% — replacement required within 48h',
    category: 'machine',
    severity: 'critical',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    read: false,
  },
  {
    id: 'n2',
    title: 'Inventory Reorder Alert',
    message: 'PROD-A has 13 days supply — approaching reorder point of 961 units',
    category: 'inventory',
    severity: 'high',
    timestamp: new Date(Date.now() - 14400000).toISOString(),
    read: false,
  },
  {
    id: 'n3',
    title: 'Supplier Contract Expiry',
    message: 'Supplier B contract expires 2026-06-30 — schedule renewal review',
    category: 'supplier',
    severity: 'medium',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    read: false,
  },
  {
    id: 'n4',
    title: 'Intelligence Report Ready',
    message: 'Weekly manufacturing report available — 3 cross-domain risks identified',
    category: 'pipeline',
    severity: 'info',
    timestamp: new Date(Date.now() - 172800000).toISOString(),
    read: true,
  },
]

export const useNotificationStore = create((set, get) => ({
  notifications: initialNotifications,

  get unreadCount() {
    return get().notifications.filter((n) => !n.read).length
  },

  addNotification: (notification) => {
    const newNotification = {
      id: `n-${Date.now()}`,
      severity: 'info',
      read: false,
      timestamp: new Date().toISOString(),
      ...notification,
    }
    set((state) => ({
      notifications: [newNotification, ...state.notifications],
    }))
  },

  markRead: (id) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
    }))
  },

  markAllRead: () => {
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
    }))
  },

  dismiss: (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }))
  },
}))
