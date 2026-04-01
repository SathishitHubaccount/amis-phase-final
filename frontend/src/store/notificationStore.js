import { create } from 'zustand'
import { apiClient } from '../lib/api'

export const useNotificationStore = create((set, get) => ({
  notifications: [],
  loaded: false,

  get unreadCount() {
    return get().notifications.filter((n) => !n.read).length
  },

  // Load notifications from backend on first call
  fetchNotifications: async () => {
    if (get().loaded) return
    try {
      const res = await apiClient.getNotifications(50)
      set({ notifications: res.data.notifications || [], loaded: true })
    } catch {
      set({ loaded: true }) // Don't block UI if backend is down
    }
  },

  addNotification: async (notification) => {
    const tempId = `n-${Date.now()}`
    const newNotification = {
      id: tempId,
      severity: 'info',
      read: false,
      timestamp: new Date().toISOString(),
      category: 'system',
      ...notification,
    }
    // Optimistic update
    set((state) => ({ notifications: [newNotification, ...state.notifications] }))
    // Persist to backend
    try {
      await apiClient.createNotification(
        newNotification.title,
        newNotification.message,
        newNotification.category,
        newNotification.severity,
      )
    } catch {
      // Keep the optimistic update even if backend fails
    }
  },

  markRead: async (id) => {
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
    }))
    try {
      await apiClient.markNotificationRead(id)
    } catch { /* optimistic, ignore */ }
  },

  markAllRead: async () => {
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
    }))
    try {
      await apiClient.markAllNotificationsRead()
    } catch { /* optimistic, ignore */ }
  },

  dismiss: async (id) => {
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    }))
    try {
      await apiClient.dismissNotification(id)
    } catch { /* optimistic, ignore */ }
  },
}))
