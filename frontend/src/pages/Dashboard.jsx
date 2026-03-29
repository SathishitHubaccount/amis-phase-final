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

  const summary = data?.data

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Command Center</h1>
          <p className="mt-1 text-sm text-gray-500">Real-time manufacturing intelligence overview</p>
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
  const demandTargetStatus = demandValue.includes('1,050') ? 'success' : 'warning'

  const inventoryValue = summary?.metrics?.inventory?.value || ''
  const inventoryDays = parseFloat(inventoryValue)
  const inventoryTargetStatus = !isNaN(inventoryDays) && inventoryDays > 14 ? 'success' : 'warning'

  const oeeValue = summary?.metrics?.machines?.oee || ''
  const oeeNum = parseFloat(oeeValue)
  const machinesTargetStatus = !isNaN(oeeNum) && oeeNum > 85 ? 'success' : 'warning'

  const attainmentValue = summary?.metrics?.production?.attainment || ''
  const attainmentNum = parseFloat(attainmentValue)
  const productionTargetStatus = !isNaN(attainmentNum) && attainmentNum > 95 ? 'success' : 'warning'

  // Operator machine status grid mock colors
  const machineStatusGrid = [
    { id: 'MCH-001', status: 'healthy' },
    { id: 'MCH-002', status: 'critical' },
    { id: 'MCH-003', status: 'healthy' },
    { id: 'MCH-004', status: 'at_risk' },
    { id: 'MCH-005', status: 'healthy' },
    { id: 'MCH-006', status: 'healthy' },
  ]

  const machineStatusColor = {
    healthy: 'bg-green-400',
    at_risk: 'bg-yellow-400',
    critical: 'bg-red-500',
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Command Center</h1>
          <p className="mt-1 text-sm text-gray-500">
            Real-time manufacturing intelligence overview
          </p>
        </div>
        {/* Role Toggle */}
        <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
          {roles.map((role) => (
            <button
              key={role}
              onClick={() => setViewRole(role)}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors capitalize ${
                viewRole === role
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
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
          <div className="grid grid-cols-3 gap-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-xl border border-green-200">
            <div className="text-sm text-gray-700">
              <span>💰 Prevented Downtime Savings: </span>
              <strong className="text-green-700">$45,000</strong>
              <span className="text-gray-500"> this month</span>
            </div>
            <div className="text-sm text-gray-700">
              <span>📦 Inventory Optimization: </span>
              <strong className="text-blue-700">$12,400</strong>
              <span className="text-gray-500"> freed</span>
            </div>
            <div className="text-sm text-gray-700">
              <span>📈 Forecast Accuracy: </span>
              <strong className="text-green-700">+23%</strong>
              <span className="text-gray-500"> vs baseline</span>
            </div>
          </div>
        </motion.div>
      )}

      {/* System Health Score */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Card className="bg-gradient-to-br from-primary-500 to-accent-500 text-white border-none">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-white/80 mb-1">System Health Score</p>
                <div className="flex items-baseline gap-3">
                  <span className="text-5xl font-bold">{summary?.system_health || 0}</span>
                  <span className="text-2xl font-medium text-white/60">/100</span>
                </div>
                <p className="text-xs text-white/70 mt-1">Target: 80+</p>
                <div className="mt-2 flex items-center gap-2">
                  {summary?.status === 'healthy' ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <AlertTriangle className="h-4 w-4" />
                  )}
                  <span className="text-sm font-medium uppercase tracking-wide">
                    {summary?.status?.replace('_', ' ') || 'Unknown'}
                  </span>
                </div>
              </div>
              <div className="h-32 w-32 relative">
                <svg className="transform -rotate-90 h-32 w-32">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="white"
                    strokeOpacity="0.2"
                    strokeWidth="12"
                    fill="none"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke="white"
                    strokeWidth="12"
                    fill="none"
                    strokeDasharray={2 * Math.PI * 56}
                    strokeDashoffset={
                      2 * Math.PI * 56 * (1 - (summary?.system_health || 0) / 100)
                    }
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
              <CardTitle>Machine Status Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4">
                {machineStatusGrid.map((machine) => (
                  <div
                    key={machine.id}
                    className={`rounded-lg p-4 text-white font-semibold text-center ${machineStatusColor[machine.status]}`}
                  >
                    <p className="text-base">{machine.id}</p>
                    <p className="text-xs mt-1 capitalize font-normal opacity-90">
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
            target="Target: 1,050/wk"
            targetStatus={demandTargetStatus}
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
            <CardTitle className="flex items-center justify-between">
              <span>Active Alerts</span>
              <Badge variant="error">{summary?.alerts?.length || 0} alerts</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!summary?.alerts || summary.alerts.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <CheckCircle className="h-12 w-12 text-green-500 mb-3" />
                <p className="text-sm font-medium text-gray-900">No active alerts</p>
                <p className="text-sm text-gray-500">All systems are operating normally</p>
              </div>
            ) : (
              <div className="space-y-3">
                {summary.alerts.map((alert, index) => (
                  <motion.div
                    key={alert.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
                    className="flex items-start gap-4 p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all"
                  >
                    <div
                      className={`mt-0.5 ${
                        alert.severity === 'critical'
                          ? 'text-red-600'
                          : alert.severity === 'high'
                          ? 'text-orange-600'
                          : 'text-yellow-600'
                      }`}
                    >
                      <AlertTriangle className="h-5 w-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                        <Badge
                          variant={alert.severity === 'critical' ? 'error' : 'warning'}
                          className="uppercase"
                        >
                          {alert.severity}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDate(alert.created_at)}
                        </span>
                        <span>•</span>
                        <span className="capitalize">{alert.category}</span>
                      </div>
                    </div>
                    <button className="px-4 py-2 text-sm font-medium text-primary-700 hover:bg-primary-50 rounded-lg transition-colors">
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
            <CardTitle className="flex items-center justify-between">
              <span>Recent Activity</span>
              <Badge variant="info">{activityData?.length || 0} recent</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {!activityData || activityData.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Clock className="h-12 w-12 text-gray-400 mb-3" />
                <p className="text-sm font-medium text-gray-900">No recent activity</p>
                <p className="text-sm text-gray-500">Activity will appear here as it occurs</p>
              </div>
            ) : (
              <div className="space-y-3">
                {activityData.map((activity, index) => (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: 0.7 + index * 0.05 }}
                    className="flex items-start gap-3 p-3 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all"
                  >
                    <div className="p-2 bg-blue-50 rounded-lg">
                      <CheckCircle className="h-4 w-4 text-blue-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                      </div>
                      <p className="text-xs text-gray-600 mb-1">{activity.details}</p>
                      <div className="flex items-center gap-3 text-xs text-gray-500">
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
      <div className="flex items-center justify-center text-sm text-gray-500">
        <Clock className="h-4 w-4 mr-1" />
        Last updated: {summary?.last_updated ? formatDate(summary.last_updated) : 'Never'}
      </div>
    </div>
  )
}

function MetricCard({ icon: Icon, title, value, subtitle, trend, status, target, targetStatus, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Card className="hover:shadow-md transition-shadow">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 rounded-lg bg-primary-50">
              <Icon className="h-5 w-5 text-primary-600" />
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
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {trend && (
              <span
                className={`flex items-center text-sm font-medium ${
                  trend.startsWith('+') ? 'text-green-600' : 'text-red-600'
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
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          {target && (
            <div className="flex items-center gap-2 mt-2">
              <span className="text-xs text-gray-400">{target}</span>
              {targetStatus && (
                <Badge
                  variant={targetStatus}
                  className="text-xs py-0"
                >
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
