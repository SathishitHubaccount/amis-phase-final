import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AnimatePresence, motion } from 'framer-motion'
import {
  LayoutDashboard,
  TrendingUp,
  Package,
  Cog,
  Factory,
  Truck,
  MessageSquare,
  Play,
  Menu,
  X,
  Bell,
  Settings,
  ChevronRight,
  LogOut,
  User,
  Users,
  CheckCheck,
  Plug,
  ClipboardList,
  GitBranch,
} from 'lucide-react'
import { cn } from '../lib/utils'
import { useNotificationStore } from '../store/notificationStore'
import { apiClient } from '../lib/api'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Run Pipeline', href: '/pipeline', icon: Play },
  { name: 'Agent Negotiation', href: '/negotiation', icon: Users },
  { name: 'Demand Intelligence', href: '/demand', icon: TrendingUp },
  { name: 'Inventory Control', href: '/inventory', icon: Package },
  { name: 'Machine Health', href: '/machines', icon: Cog },
  { name: 'Production Planning', href: '/production', icon: Factory },
  { name: 'Supplier Management', href: '/suppliers', icon: Truck },
  { name: 'Ask AMIS', href: '/chat', icon: MessageSquare },
  { name: 'Integrations', href: '/integrations', icon: Plug },
  { name: 'Audit Log', href: '/audit', icon: ClipboardList },
  { name: 'Scenarios', href: '/scenarios', icon: GitBranch },
]

function getRelativeTime(timestamp) {
  const diff = Date.now() - new Date(timestamp).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

const severityBorderColor = {
  critical: 'border-l-red-500',
  high: 'border-l-orange-500',
  medium: 'border-l-yellow-500',
  info: 'border-l-blue-500',
}

const severityBadgeVariant = {
  critical: 'error',
  high: 'warning',
  medium: 'warning',
  info: 'info',
}

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notificationPanelOpen, setNotificationPanelOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('all')

  const location = useLocation()
  const navigate = useNavigate()

  const notifications = useNotificationStore((state) => state.notifications)
  const unreadCount = useNotificationStore((state) => state.notifications.filter((n) => !n.read).length)
  const markRead = useNotificationStore((state) => state.markRead)
  const markAllRead = useNotificationStore((state) => state.markAllRead)
  const dismiss = useNotificationStore((state) => state.dismiss)

  const { data: approvalsData } = useQuery({
    queryKey: ['pending-approvals-count'],
    queryFn: async () => {
      const res = await apiClient.getPendingApprovals()
      return res.data.count
    },
    refetchInterval: 15000,
  })
  const pendingCount = approvalsData || 0
  const totalBadgeCount = unreadCount + pendingCount

  const tabs = ['all', 'critical', 'high', 'medium', 'info']

  const filteredNotifications = activeTab === 'all'
    ? notifications
    : notifications.filter((n) => n.severity === activeTab)

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  const user = JSON.parse(localStorage.getItem('user') || '{"username":"Admin","role":"admin"}')

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Mobile sidebar */}
      <div
        className={cn(
          'fixed inset-0 z-50 lg:hidden',
          sidebarOpen ? 'block' : 'hidden'
        )}
      >
        <div
          className="fixed inset-0 bg-gray-600/75"
          onClick={() => setSidebarOpen(false)}
        />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col bg-white">
          <SidebarContent navigation={navigation} location={location} />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200 overflow-y-auto">
          <SidebarContent navigation={navigation} location={location} />
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col flex-1 lg:pl-64">
        {/* Top header */}
        <header className="sticky top-0 z-10 flex h-16 shrink-0 items-center gap-x-4 border-b border-gray-200 bg-white px-4 shadow-sm sm:gap-x-6 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-gray-700 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" aria-hidden="true" />
          </button>

          {/* Breadcrumb */}
          <div className="flex flex-1 gap-x-4 self-stretch items-center">
            <div className="flex items-center gap-2 text-sm">
              <span className="text-gray-500">Plant 01</span>
              <ChevronRight className="h-4 w-4 text-gray-400" />
              <span className="font-medium text-gray-900">
                {navigation.find((item) => item.href === location.pathname)?.name || 'AMIS'}
              </span>
            </div>
          </div>

          {/* Right side actions */}
          <div className="flex items-center gap-x-4">
            {/* Notification Bell */}
            <button
              onClick={() => setNotificationPanelOpen(!notificationPanelOpen)}
              className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Bell className="h-5 w-5" />
              {totalBadgeCount > 0 && (
                <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 flex items-center justify-center text-white text-xs font-bold">
                  {totalBadgeCount > 9 ? '9+' : totalBadgeCount}
                </span>
              )}
            </button>

            <button
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
              title="Settings"
            >
              <Settings className="h-5 w-5" />
            </button>

            {/* User Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="h-8 w-8 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-semibold text-sm hover:shadow-lg transition-shadow"
              >
                {user.username?.substring(0, 2).toUpperCase() || 'AM'}
              </button>

              {/* Dropdown Menu */}
              {userMenuOpen && (
                <>
                  <div
                    className="fixed inset-0 z-10"
                    onClick={() => setUserMenuOpen(false)}
                  />
                  <div className="absolute right-0 mt-2 w-56 rounded-lg bg-white shadow-lg ring-1 ring-black ring-opacity-5 z-20">
                    <div className="p-3 border-b border-gray-200">
                      <p className="text-sm font-semibold text-gray-900">{user.full_name || user.username}</p>
                      <p className="text-xs text-gray-500">{user.email || ''}</p>
                      <p className="text-xs text-primary-600 mt-1 capitalize">{user.role || 'User'}</p>
                    </div>
                    <div className="py-1">
                      <button
                        onClick={() => {
                          setUserMenuOpen(false)
                        }}
                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        <User className="h-4 w-4" />
                        My Profile
                      </button>
                      <button
                        onClick={() => {
                          setUserMenuOpen(false)
                        }}
                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                      >
                        <Settings className="h-4 w-4" />
                        Settings
                      </button>
                    </div>
                    <div className="border-t border-gray-200 py-1">
                      <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <LogOut className="h-4 w-4" />
                        Sign Out
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <div className="py-6 px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>

      {/* Notification Panel */}
      <AnimatePresence>
        {notificationPanelOpen && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 bg-black/20 z-40"
              onClick={() => setNotificationPanelOpen(false)}
            />
            {/* Panel */}
            <motion.div
              initial={{ x: 320, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 320, opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed right-0 top-0 h-full w-80 bg-white shadow-2xl z-50 border-l border-gray-200 flex flex-col"
            >
              {/* Panel Header */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200 shrink-0">
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-semibold text-gray-900">Notifications</h2>
                  {unreadCount > 0 && (
                    <span className="inline-flex items-center justify-center h-5 w-5 rounded-full bg-red-500 text-white text-xs font-bold">
                      {unreadCount}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={markAllRead}
                    className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Mark all read"
                  >
                    <CheckCheck className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => setNotificationPanelOpen(false)}
                    className="p-1.5 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Filter Tabs */}
              <div className="flex gap-1 p-2 border-b border-gray-200 shrink-0 overflow-x-auto">
                {tabs.map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={cn(
                      'px-2.5 py-1 text-xs font-medium rounded-full whitespace-nowrap transition-colors capitalize',
                      activeTab === tab
                        ? 'bg-primary-600 text-white'
                        : 'text-gray-600 hover:bg-gray-100'
                    )}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Pending Approvals Banner */}
              {pendingCount > 0 && (
                <p className="text-xs text-orange-600 px-4 py-2 bg-orange-50 border-b border-orange-100">
                  {pendingCount} pipeline decision{pendingCount > 1 ? 's' : ''} awaiting approval →{' '}
                  <a href="/pipeline" className="underline font-medium">Review in Pipeline</a>
                </p>
              )}

              {/* Notification List */}
              <div className="flex-1 overflow-y-auto">
                {filteredNotifications.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-40 gap-2 text-center px-4">
                    <Bell className="h-8 w-8 text-gray-300" />
                    <p className="text-sm text-gray-500">No notifications</p>
                  </div>
                ) : (
                  <div className="divide-y divide-gray-100">
                    {filteredNotifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={cn(
                          'p-4 border-l-4 transition-colors',
                          severityBorderColor[notification.severity] || 'border-l-gray-300',
                          !notification.read ? 'bg-blue-50' : 'bg-white hover:bg-gray-50'
                        )}
                      >
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <p className="text-sm font-medium text-gray-900 leading-tight">
                            {notification.title}
                          </p>
                          <span
                            className={cn(
                              'inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium shrink-0',
                              notification.severity === 'critical' ? 'bg-red-100 text-red-700' :
                              notification.severity === 'high' ? 'bg-orange-100 text-orange-700' :
                              notification.severity === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                              'bg-blue-100 text-blue-700'
                            )}
                          >
                            {notification.severity}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mb-2 leading-relaxed">
                          {notification.message}
                        </p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-400">
                            {getRelativeTime(notification.timestamp)}
                          </span>
                          <div className="flex gap-1">
                            {!notification.read && (
                              <button
                                onClick={() => markRead(notification.id)}
                                className="text-xs text-primary-600 hover:text-primary-800 font-medium px-1.5 py-0.5 hover:bg-primary-50 rounded transition-colors"
                              >
                                Acknowledge
                              </button>
                            )}
                            <button
                              onClick={() => dismiss(notification.id)}
                              className="text-xs text-gray-400 hover:text-red-600 font-medium px-1.5 py-0.5 hover:bg-red-50 rounded transition-colors"
                            >
                              Dismiss
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}

function SidebarContent({ navigation, location }) {
  return (
    <>
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center px-6 border-b border-gray-200">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
            <Factory className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">AMIS</h1>
            <p className="text-xs text-gray-500">Manufacturing AI</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'group flex items-center gap-x-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              )}
            >
              <item.icon
                className={cn(
                  'h-5 w-5 shrink-0',
                  isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-600'
                )}
              />
              {item.name}
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-200 p-4">
        <div className="rounded-lg bg-gradient-to-br from-primary-50 to-accent-50 p-4">
          <p className="text-xs font-semibold text-gray-900 mb-1">System Status</p>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            <p className="text-xs text-gray-600">All systems operational</p>
          </div>
        </div>
      </div>
    </>
  )
}
