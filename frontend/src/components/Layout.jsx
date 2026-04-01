import { useState, useEffect } from 'react'
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
  ClipboardList,
  Zap,
  Activity,
  FlaskConical,
  Radio,
} from 'lucide-react'
import { cn } from '../lib/utils'
import { useNotificationStore } from '../store/notificationStore'
import { apiClient } from '../lib/api'

const navigation = [
  { name: 'Dashboard',          href: '/',            icon: LayoutDashboard, section: 'overview' },
  { name: 'Run Pipeline',       href: '/pipeline',    icon: Play,            section: 'overview' },
  { name: 'Agent Negotiation',  href: '/negotiation', icon: Users,           section: 'ai', highlight: true },
  { name: 'Ask AMIS',           href: '/chat',        icon: MessageSquare,   section: 'ai', highlight: true },
  { name: 'Demand Intelligence',href: '/demand',      icon: TrendingUp,      section: 'ops' },
  { name: 'Inventory Control',  href: '/inventory',   icon: Package,         section: 'ops' },
  { name: 'Machine Health',     href: '/machines',    icon: Cog,             section: 'ops' },
  { name: 'Production Planning',href: '/production',  icon: Factory,         section: 'ops' },
  { name: 'Supplier Management',href: '/suppliers',   icon: Truck,           section: 'ops' },
  { name: 'Audit Log',          href: '/audit',        icon: ClipboardList,   section: 'system' },
  { name: 'Evals',              href: '/evals',        icon: FlaskConical,    section: 'system' },
  { name: 'Observability',      href: '/observability',icon: Radio,           section: 'system' },
]

const sections = [
  { key: 'overview', label: 'OVERVIEW' },
  { key: 'ai',       label: 'AI AGENTS' },
  { key: 'ops',      label: 'OPERATIONS' },
  { key: 'system',   label: 'SYSTEM' },
]

function getRelativeTime(timestamp) {
  const diff = Date.now() - new Date(timestamp).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [notificationPanelOpen, setNotificationPanelOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('all')

  const location = useLocation()
  const navigate = useNavigate()

  const notifications = useNotificationStore((s) => s.notifications)
  const unreadCount = useNotificationStore((s) => s.notifications.filter((n) => !n.read).length)
  const markRead = useNotificationStore((s) => s.markRead)
  const markAllRead = useNotificationStore((s) => s.markAllRead)
  const dismiss = useNotificationStore((s) => s.dismiss)
  const fetchNotifications = useNotificationStore((s) => s.fetchNotifications)

  useEffect(() => { fetchNotifications() }, [fetchNotifications])

  const { data: approvalsData } = useQuery({
    queryKey: ['pending-approvals-count'],
    queryFn: async () => (await apiClient.getPendingApprovals()).data.count,
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
  const currentPage = navigation.find((item) => item.href === location.pathname)?.name || 'AMIS'

  return (
    <div className="flex h-screen bg-slate-950">
      {/* Mobile sidebar overlay */}
      <div className={cn('fixed inset-0 z-50 lg:hidden', sidebarOpen ? 'block' : 'hidden')}>
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
        <div className="fixed inset-y-0 left-0 flex w-64 flex-col">
          <SidebarContent navigation={navigation} sections={sections} location={location} onClose={() => setSidebarOpen(false)} />
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 z-30">
        <SidebarContent navigation={navigation} sections={sections} location={location} />
      </div>

      {/* Main content */}
      <div className="flex flex-col flex-1 lg:pl-64 min-w-0">
        {/* Top header */}
        <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-x-4 border-b border-slate-800 bg-slate-900/95 backdrop-blur px-4 sm:px-6 lg:px-8">
          <button
            type="button"
            className="-m-2.5 p-2.5 text-slate-400 lg:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-6 w-6" />
          </button>

          {/* Breadcrumb */}
          <div className="flex flex-1 items-center gap-2 text-sm min-w-0">
            <span className="text-slate-500 hidden sm:block">Plant 01</span>
            <ChevronRight className="h-4 w-4 text-slate-600 hidden sm:block" />
            <span className="font-semibold text-white truncate">{currentPage}</span>
          </div>

          {/* Live indicator */}
          <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-medium text-emerald-400">Live</span>
          </div>

          {/* Right actions */}
          <div className="flex items-center gap-2">
            {/* Notification Bell */}
            <button
              onClick={() => setNotificationPanelOpen(!notificationPanelOpen)}
              className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <Bell className="h-5 w-5" />
              {totalBadgeCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-red-500 flex items-center justify-center text-white text-[10px] font-bold">
                  {totalBadgeCount > 9 ? '9+' : totalBadgeCount}
                </span>
              )}
            </button>

            <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
              <Settings className="h-5 w-5" />
            </button>

            {/* User avatar */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="h-8 w-8 rounded-full bg-gradient-to-br from-violet-500 to-cyan-500 flex items-center justify-center text-white font-bold text-xs shadow-lg hover:shadow-violet-500/25 transition-shadow"
              >
                {user.username?.substring(0, 2).toUpperCase() || 'AM'}
              </button>

              {userMenuOpen && (
                <>
                  <div className="fixed inset-0 z-10" onClick={() => setUserMenuOpen(false)} />
                  <div className="absolute right-0 mt-2 w-56 rounded-xl bg-slate-800 border border-slate-700 shadow-2xl z-20 overflow-hidden">
                    <div className="p-3 border-b border-slate-700">
                      <p className="text-sm font-semibold text-white">{user.full_name || user.username}</p>
                      <p className="text-xs text-slate-400">{user.email || ''}</p>
                      <span className="inline-block mt-1 px-2 py-0.5 rounded-full text-xs bg-violet-500/20 text-violet-300 border border-violet-500/30 capitalize">{user.role || 'User'}</span>
                    </div>
                    <div className="py-1">
                      <button onClick={() => setUserMenuOpen(false)} className="flex items-center gap-2 w-full px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 transition-colors">
                        <User className="h-4 w-4" /> My Profile
                      </button>
                      <button onClick={() => setUserMenuOpen(false)} className="flex items-center gap-2 w-full px-4 py-2 text-sm text-slate-300 hover:bg-slate-700 transition-colors">
                        <Settings className="h-4 w-4" /> Settings
                      </button>
                    </div>
                    <div className="border-t border-slate-700 py-1">
                      <button onClick={handleLogout} className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors">
                        <LogOut className="h-4 w-4" /> Sign Out
                      </button>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto bg-slate-950">
          <div className="py-6 px-4 sm:px-6 lg:px-8">
            {children}
          </div>
        </main>
      </div>

      {/* Notification Panel */}
      <AnimatePresence>
        {notificationPanelOpen && (
          <>
            <div className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm" onClick={() => setNotificationPanelOpen(false)} />
            <motion.div
              initial={{ x: 320, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 320, opacity: 0 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed right-0 top-0 h-full w-80 bg-slate-900 border-l border-slate-800 shadow-2xl z-50 flex flex-col"
            >
              <div className="flex items-center justify-between p-4 border-b border-slate-800 shrink-0">
                <div className="flex items-center gap-2">
                  <h2 className="text-base font-semibold text-white">Notifications</h2>
                  {unreadCount > 0 && (
                    <span className="inline-flex items-center justify-center h-5 w-5 rounded-full bg-red-500 text-white text-xs font-bold">{unreadCount}</span>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  <button onClick={markAllRead} className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors" title="Mark all read">
                    <CheckCheck className="h-4 w-4" />
                  </button>
                  <button onClick={() => setNotificationPanelOpen(false)} className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors">
                    <X className="h-4 w-4" />
                  </button>
                </div>
              </div>

              <div className="flex gap-1 p-2 border-b border-slate-800 shrink-0 overflow-x-auto">
                {tabs.map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={cn(
                      'px-2.5 py-1 text-xs font-medium rounded-full whitespace-nowrap transition-colors capitalize',
                      activeTab === tab ? 'bg-violet-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                    )}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {pendingCount > 0 && (
                <p className="text-xs text-amber-400 px-4 py-2 bg-amber-500/10 border-b border-amber-500/20">
                  {pendingCount} decision{pendingCount > 1 ? 's' : ''} awaiting approval →{' '}
                  <a href="/pipeline" className="underline font-medium">Review</a>
                </p>
              )}

              <div className="flex-1 overflow-y-auto">
                {filteredNotifications.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-40 gap-2 text-center px-4">
                    <Bell className="h-8 w-8 text-slate-700" />
                    <p className="text-sm text-slate-500">No notifications</p>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-800">
                    {filteredNotifications.map((n) => (
                      <div
                        key={n.id}
                        className={cn(
                          'p-4 border-l-4 transition-colors',
                          n.severity === 'critical' ? 'border-l-red-500' :
                          n.severity === 'high'     ? 'border-l-orange-500' :
                          n.severity === 'medium'   ? 'border-l-yellow-500' : 'border-l-blue-500',
                          !n.read ? 'bg-slate-800/60' : 'hover:bg-slate-800/30'
                        )}
                      >
                        <div className="flex items-start justify-between gap-2 mb-1">
                          <p className="text-sm font-medium text-white leading-tight">{n.title}</p>
                          <span className={cn(
                            'inline-flex items-center rounded-full px-1.5 py-0.5 text-[10px] font-medium shrink-0',
                            n.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                            n.severity === 'high'     ? 'bg-orange-500/20 text-orange-400' :
                            n.severity === 'medium'   ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-blue-500/20 text-blue-400'
                          )}>{n.severity}</span>
                        </div>
                        <p className="text-xs text-slate-400 mb-2 leading-relaxed">{n.message}</p>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-slate-600">{getRelativeTime(n.timestamp)}</span>
                          <div className="flex gap-1">
                            {!n.read && (
                              <button onClick={() => markRead(n.id)} className="text-xs text-violet-400 hover:text-violet-300 font-medium px-1.5 py-0.5 hover:bg-violet-500/10 rounded transition-colors">
                                Acknowledge
                              </button>
                            )}
                            <button onClick={() => dismiss(n.id)} className="text-xs text-slate-500 hover:text-red-400 font-medium px-1.5 py-0.5 hover:bg-red-500/10 rounded transition-colors">
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

function SidebarContent({ navigation, sections, location }) {
  return (
    <div className="flex flex-col h-full bg-slate-900 border-r border-slate-800">
      {/* Logo */}
      <div className="flex h-16 shrink-0 items-center px-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-violet-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-violet-500/25">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-wide">AMIS</h1>
            <p className="text-[10px] text-slate-500 tracking-widest uppercase">Manufacturing AI</p>
          </div>
        </div>
      </div>

      {/* Navigation grouped by section */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-5">
        {sections.map(({ key, label }) => {
          const items = navigation.filter((n) => n.section === key)
          if (!items.length) return null
          return (
            <div key={key}>
              <p className="px-3 mb-1.5 text-[10px] font-semibold tracking-widest text-slate-600 uppercase">{label}</p>
              <div className="space-y-0.5">
                {items.map((item) => {
                  const isActive = location.pathname === item.href
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={cn(
                        'group flex items-center gap-x-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-150',
                        isActive
                          ? item.highlight
                            ? 'bg-gradient-to-r from-violet-600/30 to-cyan-600/10 text-white border border-violet-500/30'
                            : 'bg-slate-800 text-white'
                          : item.highlight
                            ? 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
                            : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                      )}
                    >
                      <item.icon className={cn(
                        'h-4 w-4 shrink-0 transition-colors',
                        isActive
                          ? item.highlight ? 'text-violet-400' : 'text-white'
                          : item.highlight ? 'text-violet-500 group-hover:text-violet-400' : 'text-slate-500 group-hover:text-slate-300'
                      )} />
                      <span className="truncate">{item.name}</span>
                      {item.highlight && !isActive && (
                        <span className="ml-auto shrink-0 h-1.5 w-1.5 rounded-full bg-violet-500" />
                      )}
                    </Link>
                  )
                })}
              </div>
            </div>
          )
        })}
      </nav>

      {/* Footer status */}
      <div className="border-t border-slate-800 p-4">
        <div className="rounded-xl bg-gradient-to-br from-slate-800 to-slate-800/50 border border-slate-700/50 p-3">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-slate-300">System Status</p>
            <Activity className="h-3.5 w-3.5 text-emerald-400" />
          </div>
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400" />
            <p className="text-xs text-slate-400">All systems operational</p>
          </div>
          <div className="mt-2 h-1 rounded-full bg-slate-700 overflow-hidden">
            <div className="h-full w-[94%] rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500" />
          </div>
        </div>
      </div>
    </div>
  )
}
