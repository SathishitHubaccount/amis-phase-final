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
import Card, { CardHeader, CardTitle, CardContent } from '../components/Card'
import Badge from '../components/Badge'
import { apiClient } from '../lib/api'
import { formatDate } from '../lib/utils'

const mockEntries = [
  {
    id: 'a1',
    agentType: 'MACHINE',
    title: 'MCH-002 Preventive Maintenance Recommended',
    status: 'Accepted',
    actionBy: 'Plant Manager',
    timestamp: new Date(Date.now() - 3600000).toISOString(),
    outcome: 'Prevented estimated 4h downtime ($18K)',
    detail: 'AI detected bearing vibration anomaly at 58% failure probability. Recommended immediate preventive replacement. Work order WO-2026-0421 created.',
  },
  {
    id: 'a2',
    agentType: 'INVENTORY',
    title: 'Safety stock increase for PROD-A',
    status: 'Accepted',
    actionBy: 'Supply Chain Lead',
    timestamp: new Date(Date.now() - 7200000).toISOString(),
    outcome: 'Stockout avoided — 3 days later demand spiked',
    detail: 'AI recommended increasing safety stock from 300 to 596 units based on demand variability increase. Order placed with SUP-001.',
  },
  {
    id: 'a3',
    agentType: 'DEMAND',
    title: 'Demand forecast revision: +8% Week 14',
    status: 'Modified',
    actionBy: 'Sales Director',
    timestamp: new Date(Date.now() - 14400000).toISOString(),
    outcome: 'User adjusted to +5% based on customer input',
    detail: 'AI forecast suggested +8% uplift based on historical seasonal patterns and market data. Sales team overrode to +5% after direct customer conversation.',
  },
  {
    id: 'a4',
    agentType: 'PRODUCTION',
    title: 'Overtime scheduling: 12h additional capacity',
    status: 'Accepted',
    actionBy: 'Operations Manager',
    timestamp: new Date(Date.now() - 28800000).toISOString(),
    outcome: 'Order fulfilled on time',
    detail: 'AI identified 105 unit/week gap between capacity and demand. Recommended 12 hours overtime on Line 2 and Line 3 for weeks 12-13.',
  },
  {
    id: 'a5',
    agentType: 'SUPPLIER',
    title: 'Dual-source allocation shift to SUP-A 70/30',
    status: 'Accepted',
    actionBy: 'Procurement Manager',
    timestamp: new Date(Date.now() - 43200000).toISOString(),
    outcome: 'Delivery reliability improved 12%',
    detail: 'AI recommended shifting primary allocation from 45/25/30 split to 70/30 (SUP-001/SUP-003) to reduce exposure to low-performing suppliers.',
  },
  {
    id: 'a6',
    agentType: 'MACHINE',
    title: 'MCH-004 emergency maintenance flag',
    status: 'Accepted',
    actionBy: 'Maintenance Supervisor',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    outcome: 'Line 4 restored after 18h',
    detail: 'AI detected hydraulic pressure drop anomaly on MCH-004. Emergency maintenance window opened immediately to prevent full line failure.',
  },
  {
    id: 'a7',
    agentType: 'INVENTORY',
    title: 'EOQ adjustment for SH-100 component',
    status: 'Modified',
    actionBy: 'Inventory Planner',
    timestamp: new Date(Date.now() - 172800000).toISOString(),
    outcome: 'Order quantity rounded to pallet size',
    detail: 'AI calculated optimal EOQ of 2,840 units. Planner rounded to 3,000 to match standard pallet size of 500 units, reducing handling cost.',
  },
  {
    id: 'a8',
    agentType: 'DEMAND',
    title: 'Anomaly detected W06 — spike flagged',
    status: 'Dismissed',
    actionBy: 'Demand Planner',
    timestamp: new Date(Date.now() - 259200000).toISOString(),
    outcome: 'User attributed to one-time event',
    detail: 'AI flagged unexpected 340% demand spike in Week 6 as potential data quality issue or extraordinary event. Planner confirmed it was a one-time bulk customer order.',
  },
  {
    id: 'a9',
    agentType: 'PRODUCTION',
    title: 'Capacity gap alert: 105 units/week shortfall',
    status: 'Accepted',
    actionBy: 'Plant Manager',
    timestamp: new Date(Date.now() - 345600000).toISOString(),
    outcome: 'OT authorized',
    detail: 'AI identified growing capacity gap over weeks 11-14 due to MCH-004 maintenance downtime. Overtime approved for 2 lines.',
  },
  {
    id: 'a10',
    agentType: 'SUPPLIER',
    title: 'PO-2026-021 expedite recommendation',
    status: 'Accepted',
    actionBy: 'Procurement Manager',
    timestamp: new Date(Date.now() - 432000000).toISOString(),
    outcome: 'Delivered 3 days early',
    detail: 'AI predicted stockout risk reaching 41% within 14 days based on inventory burn rate. Recommended expediting PO-2026-021 with SUP-001 at +$2,100 premium freight cost.',
  },
  {
    id: 'a11',
    agentType: 'MACHINE',
    title: 'MCH-003 hydraulic pressure monitoring alert',
    status: 'Accepted',
    actionBy: 'Maintenance Lead',
    timestamp: new Date(Date.now() - 518400000).toISOString(),
    outcome: 'Inspection scheduled',
    detail: 'AI flagged gradual hydraulic pressure decline over 7 days on MCH-003. Scheduled inspection during planned maintenance window to prevent unplanned downtime.',
  },
  {
    id: 'a12',
    agentType: 'DEMAND',
    title: 'Seasonal adjustment: +12% March forecast',
    status: 'Modified',
    actionBy: 'Sales Director',
    timestamp: new Date(Date.now() - 604800000).toISOString(),
    outcome: 'Adjusted to +9%',
    detail: 'AI seasonal model suggested +12% uplift for March based on 3-year historical pattern. Sales team moderated to +9% based on current market conditions.',
  },
]

const statusIcon = {
  Accepted: <CheckCircle className="h-4 w-4 text-green-600" />,
  Modified: <Edit2 className="h-4 w-4 text-blue-600" />,
  Dismissed: <X className="h-4 w-4 text-gray-500" />,
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
                entry.status === 'Accepted' ? 'bg-green-100 text-green-700' :
                entry.status === 'Modified' ? 'bg-blue-100 text-blue-700' :
                'bg-gray-100 text-gray-600'
              }`}
            >
              {entry.status}
            </span>
          </div>
          <p className="text-sm font-semibold text-gray-900 mb-1">{entry.title}</p>
          <div className="flex flex-wrap gap-3 text-xs text-gray-500 mb-1">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {new Date(entry.timestamp).toLocaleString()}
            </span>
            <span>By: {entry.actionBy}</span>
          </div>
          {entry.outcome && (
            <p className="text-xs text-gray-600 italic mb-1">
              Outcome: {entry.outcome}
            </p>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-800 transition-colors mt-1"
          >
            {expanded ? (
              <><ChevronUp className="h-3.5 w-3.5" /> Hide details</>
            ) : (
              <><ChevronDown className="h-3.5 w-3.5" /> Show full recommendation</>
            )}
          </button>
          {expanded && (
            <div className="mt-2 p-3 bg-gray-50 rounded-lg border border-gray-200 text-xs text-gray-700 leading-relaxed">
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

  const { data: decisionsData, isLoading } = useQuery({
    queryKey: ['decisions'],
    queryFn: async () => {
      const response = await apiClient.getDecisions(100)
      return response.data.decisions
    },
    refetchInterval: 15000,
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

  // Use real DB data if available, otherwise fall back to mock seed data
  const allEntries = decisionsData && decisionsData.length > 0
    ? decisionsData.map(normalizeDbEntry)
    : mockEntries

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
          <h1 className="text-3xl font-bold text-gray-900">Decision Audit Log</h1>
          <p className="mt-1 text-sm text-gray-500 flex items-center gap-2">
            Complete AI recommendation and user action history
            {decisionsData && decisionsData.length > 0 && (
              <span className="inline-flex items-center gap-1 text-xs font-medium text-green-700 bg-green-100 px-2 py-0.5 rounded-full">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse inline-block" />
                Live data — {decisionsData.length} recorded
              </span>
            )}
          </p>
        </div>
        <button
          onClick={() => alert('Exporting audit log to CSV...')}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center gap-2 text-sm font-medium transition-colors shrink-0"
        >
          <Download className="h-4 w-4" />
          Export CSV
        </button>
      </div>

      {/* Summary Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">{allEntries.length}</p>
            <p className="text-sm text-gray-500">Total Decisions</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-green-600">{acceptedCount}</p>
            <p className="text-sm text-gray-500">
              Accepted ({Math.round((acceptedCount / mockEntries.length) * 100)}%)
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-blue-600">{modifiedCount}</p>
            <p className="text-sm text-gray-500">
              Modified ({Math.round((modifiedCount / mockEntries.length) * 100)}%)
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <p className="text-2xl font-bold text-gray-500">{dismissedCount}</p>
            <p className="text-sm text-gray-500">
              Dismissed ({Math.round((dismissedCount / mockEntries.length) * 100)}%)
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filter Bar */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-3 items-center">
            <div className="relative flex-1 min-w-48">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Search decisions..."
                className="w-full pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 bg-white"
            >
              {categories.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 bg-white"
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
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({filteredEntries.length} entries)
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {filteredEntries.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No entries match your filters.</p>
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
