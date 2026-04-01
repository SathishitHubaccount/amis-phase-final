import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  Package,
  Cog,
  Factory,
  AlertTriangle,
  CheckCircle,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'
import {
  LineChart, Line, ResponsiveContainer,
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip,
} from 'recharts'
import Card, { CardHeader, CardTitle, CardContent } from '../components/Card'
import Badge from '../components/Badge'
import { SkeletonMetricCard } from '../components/Skeleton'
import ErrorState from '../components/ErrorState'
import { apiClient } from '../lib/api'
import { formatNumber, formatDate, getSeverityColor } from '../lib/utils'

export default function Dashboard() {
  const [viewRole, setViewRole] = useState('manager')
  const roles = ['operator', 'manager', 'executive']

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => apiClient.getDashboardSummary(),
    refetchInterval: 30000,
    retry: 3,
    retryDelay: 2000,
  })

  const { data: activityData } = useQuery({
    queryKey: ['activity-log'],
    queryFn: async () => {
      const response = await apiClient.getActivityLog(10)
      return response.data.activities
    },
    refetchInterval: 30000,
  })

  const { data: trendsData } = useQuery({
    queryKey: ['dashboard-trends'],
    queryFn: () => apiClient.getDashboardTrends(),
    refetchInterval: 60000,
  })

  const { data: roiData } = useQuery({
    queryKey: ['dashboard-roi'],
    queryFn: () => apiClient.getDashboardROI(),
    refetchInterval: 120000,
  })

  const summary = data?.data

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Command Center</h1>
          <p className="mt-1 text-sm text-slate-400">Real-time manufacturing intelligence overview</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <SkeletonMetricCard />
          <SkeletonMetricCard />
          <SkeletonMetricCard />
          <SkeletonMetricCard />
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <ErrorState
        title="Cannot connect to backend"
        message="Make sure the backend server is running on port 8000"
        onRetry={() => refetch()}
      />
    )
  }

  // Derive target statuses from summary data
  const demandValue = summary?.metrics?.demand?.value || ''
  const demandNum = parseInt((demandValue).replace(/[^\d]/g, '')) || 0
  const demandTargetStatus = demandNum >= 1000 ? 'success' : 'warning'

  const inventoryValue = summary?.metrics?.inventory?.value || ''
  const inventoryDays = parseFloat(inventoryValue)
  const inventoryTargetStatus = !isNaN(inventoryDays) && inventoryDays > 14 ? 'success' : 'warning'

  const oeeValue = summary?.metrics?.machines?.oee || ''
  const oeeNum = parseFloat(oeeValue)
  const machinesTargetStatus = !isNaN(oeeNum) && oeeNum > 85 ? 'success' : 'warning'

  const attainmentValue = summary?.metrics?.production?.attainment || ''
  const attainmentNum = parseFloat(attainmentValue)
  const productionTargetStatus = !isNaN(attainmentNum) && attainmentNum > 95 ? 'success' : 'warning'

  const machineStatusColor = {
    healthy: 'bg-emerald-500/20 border border-emerald-500/30 text-emerald-400',
    at_risk: 'bg-amber-500/20 border border-amber-500/30 text-amber-400',
    critical: 'bg-red-500/20 border border-red-500/30 text-red-400',
  }

  // Real machine grid from DB (used in operator view)
  const machineStatusGrid = summary?.metrics?.machines?.all_machines ||
    summary?.metrics?.machines?.critical_machines?.map((id) => ({ id, status: 'critical' })) || []

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold text-white">Command Center</h1>
          <p className="mt-1 text-sm text-slate-400">
            Real-time manufacturing intelligence overview
          </p>
        </div>
        {/* Role Toggle */}
        <div className="flex items-center gap-1 bg-slate-800 rounded-lg p-1 border border-slate-700">
          {roles.map((role) => (
            <button
              key={role}
              onClick={() => setViewRole(role)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors capitalize ${
                viewRole === role
                  ? 'bg-slate-700 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {role}
            </button>
          ))}
        </div>
      </div>

      {/* Executive ROI Row */}
      {viewRole === 'executive' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4 p-4 bg-gradient-to-r from-emerald-500/10 to-blue-500/10 rounded-xl border border-emerald-500/20">
              <div className="text-sm text-slate-300">
                <span>💰 Prevented Downtime Savings: </span>
                <strong className="text-emerald-400">
                  {roiData?.data?.downtime_savings_formatted ?? '—'}
                </strong>
                <span className="text-slate-500"> this month</span>
              </div>
              <div className="text-sm text-slate-300">
                <span>📦 Inventory Optimization: </span>
                <strong className="text-blue-400">
                  {roiData?.data?.inventory_freed_formatted ?? '—'}
                </strong>
                <span className="text-slate-500"> freed</span>
              </div>
              <div className="text-sm text-slate-300">
                <span>📈 AI Decisions Accepted: </span>
                <strong className="text-emerald-400">
                  {roiData?.data?.acceptance_rate ?? '—'}
                </strong>
                <span className="text-slate-500"> acceptance rate</span>
              </div>
            </div>

            {/* Cross-Domain Risk Bubble Chart */}
            <Card>
              <CardContent className="p-4">
                <p className="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                  Cross-Domain Risk Map — Probability vs Business Impact
                </p>
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 30 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis type="number" dataKey="x" name="Probability" domain={[0, 100]} tick={{ fontSize: 10, fill: '#94a3b8' }}
                        label={{ value: 'Probability %', position: 'insideBottom', offset: -10, fontSize: 10, fill: '#64748b' }} />
                      <YAxis type="number" dataKey="y" name="Impact ($K)" domain={[0, 60]} tick={{ fontSize: 10, fill: '#94a3b8' }}
                        label={{ value: 'Impact ($K)', angle: -90, position: 'insideLeft', fontSize: 10, fill: '#64748b' }} />
                      <ZAxis type="number" dataKey="z" range={[60, 300]} />
                      <Tooltip
                        content={({ payload }) => {
                          if (!payload?.length) return null
                          const d = payload[0].payload
                          return (
                            <div className="bg-slate-800 border border-slate-700 rounded-lg p-2 shadow text-xs">
                              <p className="font-semibold text-white">{d.name}</p>
                              <p className="text-slate-400">Prob: {d.x}% | Impact: ${d.y}K</p>
                            </div>
                          )
                        }}
                      />
                      <Scatter
                        data={[
                          { x: summary?.metrics?.machines?.critical_machines?.length > 0 ? 65 : 18, y: 45, z: 120, name: 'Machine Failure Risk', fill: '#dc2626' },
                          { x: summary?.metrics?.inventory?.below_rop > 0 ? 55 : 12, y: 28, z: 90, name: 'Inventory Stockout', fill: '#f59e0b' },
                          { x: 35, y: 18, z: 70, name: 'Supplier Delay', fill: '#3b82f6' },
                          { x: 20, y: 38, z: 80, name: 'Demand Spike', fill: '#8b5cf6' },
                          { x: parseFloat(oeeValue) < 80 ? 48 : 15, y: 22, z: 60, name: 'OEE Degradation', fill: '#f97316' },
                        ].map(d => ({ ...d, x: d.x, y: d.y, z: d.z }))}
                        shape={(props) => {
                          const { cx, cy, fill } = props
                          const r = Math.sqrt((props.z || 80) / Math.PI) * 1.8
                          return <circle cx={cx} cy={cy} r={r} fill={fill} fillOpacity={0.7} stroke={fill} strokeWidth={1.5} />
                        }}
                      />
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex flex-wrap gap-3 mt-1 justify-center text-xs text-slate-500">
                  {[
                    { color: '#dc2626', label: 'Machine Failure' },
                    { color: '#f59e0b', label: 'Inventory Stockout' },
                    { color: '#3b82f6', label: 'Supplier Delay' },
                    { color: '#8b5cf6', label: 'Demand Spike' },
                    { color: '#f97316', label: 'OEE Degradation' },
                  ].map(({ color, label }) => (
                    <span key={label} className="flex items-center gap-1">
                      <span className="h-2.5 w-2.5 rounded-full inline-block" style={{ backgroundColor: color }} />
                      {label}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </motion.div>
      )}

      {/* System Health Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card className="bg-gradient-to-br from-primary-600 to-accent-600 border-none">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-white/80 mb-1">System Health Score</p>
                <div className="flex items-baseline gap-3">
                  <span className="text-5xl font-bold text-white">{summary?.system_health || 0}</span>
                  <span className="text-2xl font-medium text-white/50">/100</span>
                </div>
                <p className="text-xs text-white/60 mt-1">Target: 80+</p>
                <div className="mt-2 flex items-center gap-2">
                  {summary?.status === 'healthy' ? (
                    <CheckCircle className="h-4 w-4 text-white" />
                  ) : (
                    <AlertTriangle className="h-4 w-4 text-white" />
                  )}
                  <span className="text-sm font-medium uppercase tracking-wide text-white">
                    {summary?.status?.replace('_', ' ') || 'Unknown'}
                  </span>
                </div>
              </div>
              <div className="h-32 w-32 relative">
                <svg className="transform -rotate-90 h-32 w-32">
                  <circle cx="64" cy="64" r="56" stroke="white" strokeOpacity="0.2" strokeWidth="12" fill="none" />
                  <circle
                    cx="64" cy="64" r="56" stroke="white" strokeWidth="12" fill="none"
                    strokeDasharray={2 * Math.PI * 56}
                    strokeDashoffset={2 * Math.PI * 56 * (1 - (summary?.system_health || 0) / 100)}
                    strokeLinecap="round"
                    className="transition-all duration-1000"
                  />
                </svg>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Operator Machine Status Grid */}
      {viewRole === 'operator' ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="text-white">Machine Status Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                {machineStatusGrid.map((machine) => (
                  <div
                    key={machine.id}
                    className={`rounded-lg p-4 font-semibold text-center ${machineStatusColor[machine.status] || 'bg-slate-800 text-slate-300'}`}
                  >
                    <p className="text-base">{machine.id}</p>
                    <p className="text-xs mt-1 capitalize font-normal opacity-80">
                      {machine.status.replace('_', ' ')}
                    </p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ) : (
        /* Key Metrics Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            icon={TrendingUp}
            title="Demand"
            value={summary?.metrics?.demand?.value || '-'}
            trend={summary?.metrics?.demand?.trend}
            status={summary?.metrics?.demand?.status}
            target="Target: 1,750/wk"
            targetStatus={demandTargetStatus}
            sparkData={trendsData?.data?.trends}
            sparkKey="demand"
            sparkColor="#3b82f6"
            iconColor="text-blue-400"
            iconBg="bg-blue-500/10"
            delay={0.1}
          />
          <MetricCard
            icon={Package}
            title="Inventory"
            value={summary?.metrics?.inventory?.value || '-'}
            subtitle={`${summary?.metrics?.inventory?.below_rop || 0} below ROP`}
            status={summary?.metrics?.inventory?.status}
            target="Target: >14 days"
            targetStatus={inventoryTargetStatus}
            sparkData={trendsData?.data?.trends}
            sparkKey="inventory"
            sparkColor="#8b5cf6"
            iconColor="text-violet-400"
            iconBg="bg-violet-500/10"
            delay={0.2}
          />
          <MetricCard
            icon={Cog}
            title="Machines"
            value={summary?.metrics?.machines?.oee || '-'}
            subtitle={
              summary?.metrics?.machines?.critical_machines?.length > 0
                ? `${summary.metrics.machines.critical_machines[0]} critical`
                : 'All operational'
            }
            status={summary?.metrics?.machines?.status}
            target="Target: OEE >85%"
            targetStatus={machinesTargetStatus}
            sparkData={trendsData?.data?.trends}
            sparkKey="oee"
            sparkColor="#10b981"
            iconColor="text-emerald-400"
            iconBg="bg-emerald-500/10"
            delay={0.3}
          />
          <MetricCard
            icon={Factory}
            title="Production"
            value={summary?.metrics?.production?.attainment || '-'}
            subtitle={`Gap: ${summary?.metrics?.production?.gap || 0} units`}
            status={summary?.metrics?.production?.status}
            target="Target: >95%"
            targetStatus={productionTargetStatus}
            sparkData={trendsData?.data?.trends}
            sparkKey="attainment"
            sparkColor="#f59e0b"
            iconColor="text-amber-400"
            iconBg="bg-amber-500/10"
            delay={0.4}
          />
        </div>
      )}

      {/* Alerts Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between text-white">
              <span>Active Alerts</span>
              <Badge variant="error">{summary?.alerts?.length || 0} alerts</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!summary?.alerts || summary.alerts.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <CheckCircle className="h-12 w-12 text-emerald-500 mb-3" />
                <p className="text-sm font-medium text-white">No active alerts</p>
                <p className="text-sm text-slate-400">All systems are operating normally</p>
              </div>
            ) : (
              <div className="space-y-3">
                {summary.alerts.map((alert, index) => (
                  <motion.div
                    key={alert.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
                    className="flex items-start gap-4 p-4 rounded-lg border border-slate-800 hover:border-slate-700 hover:bg-slate-800/50 transition-all"
                  >
                    <div
                      className={`mt-0.5 ${
                        alert.severity === 'critical'
                          ? 'text-red-400'
                          : alert.severity === 'high'
                          ? 'text-orange-400'
                          : 'text-amber-400'
                      }`}
                    >
                      <AlertTriangle className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium text-white">{alert.title}</p>
                        <Badge
                          variant={alert.severity === 'critical' ? 'error' : 'warning'}
                          className="uppercase"
                        >
                          {alert.severity}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDate(alert.created_at)}
                        </span>
                        <span>•</span>
                        <span className="capitalize">{alert.category}</span>
                      </div>
                    </div>
                    <button className="px-4 py-2 text-sm font-medium text-primary-400 hover:bg-primary-500/10 rounded-lg transition-colors border border-primary-500/20">
                      Review
                    </button>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Activity Log */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between text-white">
              <span>Recent Activity</span>
              <Badge variant="info">{activityData?.length || 0} recent</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!activityData || activityData.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Clock className="h-12 w-12 text-slate-600 mb-3" />
                <p className="text-sm font-medium text-white">No recent activity</p>
                <p className="text-sm text-slate-400">Activity will appear here as it occurs</p>
              </div>
            ) : (
              <div className="space-y-3">
                {activityData.map((activity, index) => (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.7 + index * 0.05 }}
                    className="flex items-start gap-3 p-3 rounded-lg border border-slate-800 hover:border-slate-700 hover:bg-slate-800/50 transition-all"
                  >
                    <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                      <CheckCircle className="h-4 w-4 text-blue-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium text-white">{activity.action}</p>
                      </div>
                      <p className="text-xs text-slate-400 mb-1">{activity.details}</p>
                      <div className="flex items-center gap-3 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDate(activity.timestamp)}
                        </span>
                        <span>•</span>
                        <span>{activity.user}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Last Updated */}
      <div className="flex items-center justify-center text-sm text-slate-500">
        <Clock className="h-4 w-4 mr-1" />
        Last updated: {summary?.last_updated ? formatDate(summary.last_updated) : 'Never'}
      </div>
    </div>
  )
}

function MetricCard({ icon: Icon, title, value, subtitle, trend, status, target, targetStatus, sparkData, sparkKey, sparkColor, iconColor, iconBg, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Card className="hover:border-slate-700 transition-all hover:shadow-lg hover:shadow-black/20">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-3">
            <div className={`p-2 rounded-lg ${iconBg || 'bg-primary-500/10'}`}>
              <Icon className={`h-5 w-5 ${iconColor || 'text-primary-400'}`} />
            </div>
            {status && (
              <Badge
                variant={
                  status === 'healthy'
                    ? 'success'
                    : status === 'watch'
                    ? 'warning'
                    : 'error'
                }
                className="uppercase text-xs"
              >
                {status}
              </Badge>
            )}
          </div>
          <p className="text-sm font-medium text-slate-400 mb-1">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-2xl font-bold text-white">{value}</p>
            {trend && (
              <span
                className={`flex items-center text-sm font-medium ${
                  trend.startsWith('+') ? 'text-emerald-400' : 'text-red-400'
                }`}
              >
                {trend.startsWith('+') ? (
                  <ArrowUpRight className="h-4 w-4" />
                ) : (
                  <ArrowDownRight className="h-4 w-4" />
                )}
                {trend}
              </span>
            )}
          </div>
          {subtitle && <p className="text-sm text-slate-500 mt-1">{subtitle}</p>}

          {/* 7-Day Sparkline */}
          {sparkData && sparkData.length > 0 && (
            <div className="mt-2 h-10">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sparkData} margin={{ top: 2, right: 2, left: 2, bottom: 2 }}>
                  <Line
                    type="monotone"
                    dataKey={sparkKey}
                    stroke={sparkColor || '#3b82f6'}
                    strokeWidth={1.5}
                    dot={false}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          {target && (
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs text-slate-500">{target}</span>
              {targetStatus && (
                <Badge variant={targetStatus} className="text-xs py-0">
                  {targetStatus === 'success' ? 'On target' : 'Below target'}
                </Badge>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}
