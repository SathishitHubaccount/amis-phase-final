import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  CheckCircle,
  Edit2,
  X,
  ChevronDown,
  ChevronUp,
  Clock,
  Download,
  Search,
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import Card, { CardHeader, CardTitle, CardContent } from '../components/Card'
import Badge from '../components/Badge'
import { apiClient } from '../lib/api'
import { formatDate } from '../lib/utils'

const statusIcon = {
  Accepted: <CheckCircle className="h-4 w-4 text-emerald-400" />,
  Modified: <Edit2 className="h-4 w-4 text-blue-400" />,
  Dismissed: <X className="h-4 w-4 text-slate-500" />,
}

const statusBorderColor = {
  Accepted: 'border-l-green-500',
  Modified: 'border-l-blue-500',
  Dismissed: 'border-l-gray-400',
}

const agentBadgeVariant = {
  MACHINE: 'warning',
  INVENTORY: 'info',
  DEMAND: 'default',
  PRODUCTION: 'success',
  SUPPLIER: 'error',
}

function AuditEntry({ entry }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      className={`border-l-4 pl-4 pb-4 ${statusBorderColor[entry.status] || 'border-l-gray-300'}`}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5 shrink-0">{statusIcon[entry.status]}</div>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <Badge variant={agentBadgeVariant[entry.agentType] || 'default'} className="text-xs uppercase">
              {entry.agentType}
            </Badge>
            <span
              className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                entry.status === 'Accepted' ? 'bg-emerald-500/15 text-emerald-400' :
                entry.status === 'Modified' ? 'bg-blue-500/15 text-blue-400' :
                'bg-slate-800 text-slate-400'
              }`}
            >
              {entry.status}
            </span>
          </div>
          <p className="text-sm font-semibold text-white mb-1">{entry.title}</p>
          <div className="flex flex-wrap gap-3 text-xs text-slate-500 mb-1">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(entry.timestamp).toLocaleString()}
            </span>
            <span>By: {entry.actionBy}</span>
          </div>
          {entry.outcome && (
            <p className="text-xs text-slate-400 italic mb-1">
              Outcome: {entry.outcome}
            </p>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300 transition-colors mt-1"
          >
            {expanded ? (
              <><ChevronUp className="h-3.5 w-3.5" /> Hide details</>
            ) : (
              <><ChevronDown className="h-3.5 w-3.5" /> Show full recommendation</>
            )}
          </button>
          {expanded && (
            <div className="mt-2 p-3 bg-slate-700 rounded-lg border border-slate-700 text-xs text-slate-300 leading-relaxed">
              {entry.detail}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AuditLog() {
  const [searchText, setSearchText] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('All')
  const [statusFilter, setStatusFilter] = useState('All')

  const { data: decisionsData, isLoading, refetch } = useQuery({
    queryKey: ['decisions'],
    queryFn: async () => {
      const response = await apiClient.getDecisions(200)
      return response.data.decisions
    },
    refetchInterval: 5000,
    refetchOnWindowFocus: true,
    staleTime: 0,
  })

  // Normalize DB rows to the same shape as mockEntries
  const normalizeDbEntry = (row) => ({
    id: String(row.id),
    agentType: (row.agent_type || 'DEMAND').toUpperCase(),
    title: row.title,
    status: row.status,
    actionBy: row.action_by,
    timestamp: row.timestamp,
    outcome: row.note ? `Manager note: ${row.note}` : '',
    detail: row.detail || '',
  })

  const allEntries = (decisionsData || []).map(normalizeDbEntry)

  const categories = ['All', 'Demand', 'Inventory', 'Machine', 'Production', 'Supplier', 'Scenario']
  const statuses = ['All', 'Accepted', 'Modified', 'Dismissed']

  const filteredEntries = allEntries.filter((entry) => {
    const matchesSearch =
      !searchText ||
      entry.title.toLowerCase().includes(searchText.toLowerCase()) ||
      entry.detail.toLowerCase().includes(searchText.toLowerCase())
    const matchesCategory =
      categoryFilter === 'All' ||
      entry.agentType === categoryFilter.toUpperCase()
    const matchesStatus =
      statusFilter === 'All' || entry.status === statusFilter
    return matchesSearch && matchesCategory && matchesStatus
  })

  const acceptedCount = allEntries.filter((e) => e.status === 'Accepted').length
  const modifiedCount = allEntries.filter((e) => e.status === 'Modified').length
  const dismissedCount = allEntries.filter((e) => e.status === 'Dismissed').length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Decision Audit Log</h1>
          <p className="mt-1 text-sm text-slate-500 flex items-center gap-2">
            Complete AI recommendation and user action history
            {decisionsData && decisionsData.length > 0 && (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse inline-block" />
                Live data — {decisionsData.length} recorded
              </span>
            )}
          </p>
        </div>
        <button
          onClick={() => alert('Exporting audit log to CSV...')}
          className="px-4 py-2 border border-slate-700 text-slate-300 rounded-lg hover:bg-slate-700 flex items-center gap-2 text-sm font-medium transition-colors shrink-0"
        >
          <Download className="h-4 w-4" />
          Export CSV
        </button>
      </div>

      {/* Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-white">{allEntries.length}</p>
            <p className="text-sm text-slate-500">Total Decisions</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-emerald-400">{acceptedCount}</p>
            <p className="text-sm text-slate-500">
              Accepted {allEntries.length > 0 ? `(${Math.round((acceptedCount / allEntries.length) * 100)}%)` : ''}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-blue-400">{modifiedCount}</p>
            <p className="text-sm text-slate-500">
              Modified {allEntries.length > 0 ? `(${Math.round((modifiedCount / allEntries.length) * 100)}%)` : ''}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-slate-500">{dismissedCount}</p>
            <p className="text-sm text-slate-500">
              Dismissed {allEntries.length > 0 ? `(${Math.round((dismissedCount / allEntries.length) * 100)}%)` : ''}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Decision Outcome Tracker Chart */}
      {allEntries.length > 0 && (() => {
        const agents = ['MACHINE', 'INVENTORY', 'DEMAND', 'PRODUCTION', 'SUPPLIER']
        const chartData = agents.map(agent => {
          const agentEntries = allEntries.filter(e => e.agentType === agent)
          const total = agentEntries.length
          return {
            agent: agent.charAt(0) + agent.slice(1).toLowerCase(),
            Accepted: agentEntries.filter(e => e.status === 'Accepted').length,
            Modified: agentEntries.filter(e => e.status === 'Modified').length,
            Dismissed: agentEntries.filter(e => e.status === 'Dismissed').length,
            total,
          }
        }).filter(d => d.total > 0)

        const totalAccepted = allEntries.filter(e => e.status === 'Accepted').length
        const totalModified = allEntries.filter(e => e.status === 'Modified').length
        const totalDismissed = allEntries.filter(e => e.status === 'Dismissed').length

        return (
          <Card className="overflow-hidden">
            {/* Gradient header */}
            <div className="px-6 py-5 bg-gradient-to-r from-slate-800 to-slate-900 border-b border-slate-700">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-xl bg-emerald-500/15 border border-emerald-500/25">
                    <CheckCircle className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">Decision Outcome Tracker</h3>
                    <p className="text-xs text-slate-400 mt-0.5">How managers handled AI recommendations per domain</p>
                  </div>
                </div>
                {/* Summary pills */}
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-lg">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 inline-block" />
                    <span className="text-sm font-bold text-emerald-400">{totalAccepted}</span>
                    <span className="text-xs text-slate-400">Accepted</span>
                  </div>
                  <div className="flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 px-3 py-1.5 rounded-lg">
                    <span className="h-2 w-2 rounded-full bg-blue-400 inline-block" />
                    <span className="text-sm font-bold text-blue-400">{totalModified}</span>
                    <span className="text-xs text-slate-400">Modified</span>
                  </div>
                  <div className="flex items-center gap-2 bg-slate-700/50 border border-slate-600 px-3 py-1.5 rounded-lg">
                    <span className="h-2 w-2 rounded-full bg-slate-400 inline-block" />
                    <span className="text-sm font-bold text-slate-300">{totalDismissed}</span>
                    <span className="text-xs text-slate-400">Dismissed</span>
                  </div>
                </div>
              </div>
            </div>
            <CardContent className="pt-6 pb-4">
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={chartData}
                    margin={{ top: 10, right: 30, left: 0, bottom: 5 }}
                    barSize={52}
                    barCategoryGap="35%"
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis
                      dataKey="agent"
                      tick={{ fontSize: 13, fill: '#94a3b8', fontWeight: 600 }}
                      axisLine={{ stroke: '#334155' }}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 12, fill: '#64748b' }}
                      axisLine={false}
                      tickLine={false}
                      allowDecimals={false}
                    />
                    <Tooltip
                      cursor={{ fill: 'rgba(148,163,184,0.06)', radius: 8 }}
                      contentStyle={{
                        borderRadius: 12,
                        fontSize: 13,
                        background: '#0f172a',
                        border: '1px solid #334155',
                        color: '#e2e8f0',
                        padding: '10px 14px',
                        boxShadow: '0 8px 24px rgba(0,0,0,0.4)',
                      }}
                      formatter={(value, name) => [
                        <span style={{ fontWeight: 700 }}>{value}</span>,
                        name
                      ]}
                      labelStyle={{ color: '#94a3b8', fontWeight: 600, marginBottom: 4 }}
                    />
                    <Bar dataKey="Accepted" stackId="a" fill="#10b981" radius={[0, 0, 0, 0]}>
                    </Bar>
                    <Bar dataKey="Modified" stackId="a" fill="#6366f1" radius={[0, 0, 0, 0]} />
                    <Bar dataKey="Dismissed" stackId="a" fill="#475569" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              {/* Custom legend */}
              <div className="flex items-center justify-center gap-6 mt-2">
                {[
                  { color: '#10b981', label: 'Accepted', desc: 'AI recommendation applied as-is' },
                  { color: '#6366f1', label: 'Modified', desc: 'Applied with manager edits' },
                  { color: '#475569', label: 'Dismissed', desc: 'Recommendation overridden' },
                ].map(({ color, label, desc }) => (
                  <div key={label} className="flex items-center gap-2">
                    <span className="h-3 w-3 rounded-sm inline-block shrink-0" style={{ backgroundColor: color }} />
                    <span className="text-sm font-semibold text-slate-300">{label}</span>
                    <span className="text-xs text-slate-500 hidden sm:inline">— {desc}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )
      })()}

      {/* Filter Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-3 items-center">
            <div className="relative flex-1 min-w-48">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
              <input
                type="text"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Search decisions..."
                className="w-full pl-9 pr-4 py-2 border border-slate-700 rounded-lg text-sm bg-slate-900 text-white placeholder-slate-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:bg-slate-900 focus:outline-none"
              />
            </div>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 border border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 bg-slate-900"
            >
              {categories.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-slate-700 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 bg-slate-900"
            >
              {statuses.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>
            Decision Timeline
            <span className="ml-2 text-sm font-normal text-slate-500">
              ({filteredEntries.length} entries)
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredEntries.length === 0 ? (
            <p className="text-center text-slate-500 py-8">No entries match your filters.</p>
          ) : (
            <div className="space-y-6">
              {filteredEntries.map((entry, idx) => (
                <motion.div
                  key={entry.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: idx * 0.04 }}
                >
                  <AuditEntry entry={entry} />
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
