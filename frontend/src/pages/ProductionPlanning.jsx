import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Factory, TrendingUp, Clock, Users, Play, Loader2, CheckCircle, AlertTriangle, Edit } from 'lucide-react'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import ExportButton from '../components/ExportButton'
import ScheduleEditModal from '../components/ScheduleEditModal'
import RecommendationCard from '../components/RecommendationCard'
import { apiClient } from '../lib/api'
import { formatNumber } from '../lib/utils'

export default function ProductionPlanning() {
  const [productId, setProductId] = useState('PROD-A')
  const [result, setResult] = useState(null)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedRow, setSelectedRow] = useState(null)
  const queryClient = useQueryClient()
  const currentUser = JSON.parse(localStorage.getItem('user') || '{"username":"Admin"}')

  // Fetch products for dropdown
  const { data: productsData } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await apiClient.getProducts()
      return response.data.products
    },
  })

  // Fetch production lines from database
  const { data: linesData, isLoading: linesLoading } = useQuery({
    queryKey: ['production-lines', productId],
    queryFn: async () => {
      const response = await apiClient.getProductionLines(productId)
      return response.data.production_lines
    },
  })

  // Fetch production schedule from database
  const { data: scheduleData, isLoading: scheduleLoading } = useQuery({
    queryKey: ['production-schedule', productId],
    queryFn: async () => {
      const response = await apiClient.getProductionSchedule(productId, 4)
      return response.data.schedule
    },
  })

  const runProductionAnalysis = useMutation({
    mutationFn: () => apiClient.runAgent('production',
      `Provide complete production planning analysis including Master Production Schedule (MPS), bottleneck analysis, capacity gaps, overtime recommendations, and BOM/MRP insights for ${productId}`,
      productId
    ),
    onSuccess: async (data) => {
      const runId = data.data.run_id
      pollForResult(runId)
    },
  })

  const pollForResult = async (runId) => {
    const maxAttempts = 60
    let attempts = 0

    const poll = async () => {
      try {
        const response = await apiClient.getAgentRun(runId)
        const run = response.data

        if (run.status === 'completed') {
          setResult(run.result)
        } else if (run.status === 'failed') {
          setResult(`Error: ${run.error}`)
        } else if (attempts < maxAttempts) {
          attempts++
          setTimeout(poll, 2000)
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }

    poll()
  }

  const handleEditSchedule = (row) => {
    setSelectedRow(row)
    setShowEditModal(true)
  }

  const handleSaveSchedule = async (scheduleId, updates) => {
    try {
      await apiClient.updateProductionSchedule(scheduleId, updates)
      queryClient.invalidateQueries(['production-schedule'])
      setShowEditModal(false)
      alert('Schedule updated successfully!')
    } catch (error) {
      console.error('Error updating schedule:', error)
      alert('Failed to update schedule')
    }
  }

  // Use production lines from database
  const productionLines = linesData || []
  const weeklySchedule = scheduleData || []

  // Calculate metrics dynamically from real data
  const operationalLines = productionLines.filter(l => l.status === 'running')
  const avgUtilization = operationalLines.length > 0
    ? Math.round(operationalLines.reduce((sum, l) => sum + l.utilization, 0) / operationalLines.length)
    : 0

  const totalOvertimeHours = weeklySchedule.reduce((sum, week) => sum + (week.overtime_hours || 0), 0)

  const bottleneckMachines = productionLines
    .filter(l => l.bottleneck_machine_id)
    .map(l => l.bottleneck_machine_id)
  const uniqueBottlenecks = [...new Set(bottleneckMachines)]

  // Calculate weekly capacity from production lines
  const weeklyCapacity = operationalLines.reduce((sum, line) => {
    const hoursPerWeek = 40 // 5 days * 8 hours
    return sum + (line.capacity_per_hour * hoursPerWeek)
  }, 0)

  const totalCapacityLoss = productionLines
    .filter(l => l.status === 'maintenance')
    .reduce((sum, line) => sum + (line.capacity_per_hour * 40), 0)

  return (
    <div className="space-y-6">
      {/* Page Header with Product Selector */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Production Planning</h1>
          <p className="mt-1 text-sm text-gray-500">
            Master production schedule, capacity planning, and bottleneck analysis
          </p>
        </div>
        <div className="w-64">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Product
          </label>
          <select
            value={productId}
            onChange={(e) => setProductId(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white text-sm font-medium"
          >
            {productsData?.map((product) => (
              <option key={product.id} value={product.id}>
                {product.id} - {product.name}
              </option>
            ))}
          </select>
        </div>
        <ExportButton
          endpoint={`/api/export/production/${productId}`}
          label="Export Schedule"
        />
      </div>

      {/* Quick Metrics - Now Dynamic */}
      {linesLoading || scheduleLoading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <MetricCard
            icon={Factory}
            title="Weekly Capacity"
            value={`${formatNumber(weeklyCapacity)} units`}
            subtitle={`${operationalLines.length} lines operational`}
            color="blue"
          />
          <MetricCard
            icon={TrendingUp}
            title="Avg Utilization"
            value={`${avgUtilization}%`}
            subtitle={avgUtilization >= 75 ? 'Above target (75%)' : 'Below target (75%)'}
            color={avgUtilization >= 75 ? 'green' : 'orange'}
          />
          <MetricCard
            icon={Clock}
            title="Overtime Needed"
            value={`${Math.round(totalOvertimeHours)} hours`}
            subtitle="Next 4 weeks"
            color={totalOvertimeHours > 20 ? 'orange' : 'green'}
          />
          <MetricCard
            icon={Users}
            title="Bottlenecks"
            value={`${uniqueBottlenecks.length} machines`}
            subtitle={uniqueBottlenecks.length > 0 ? uniqueBottlenecks.join(', ') : 'No bottlenecks'}
            color={uniqueBottlenecks.length > 0 ? 'red' : 'green'}
          />
        </div>
      )}

      {/* Analysis Tool */}
      <Card>
        <CardHeader>
          <CardTitle>Run Production Planning Analysis</CardTitle>
          <CardDescription>
            Get AI-powered MPS optimization, bottleneck resolution, and capacity recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <button
            onClick={() => runProductionAnalysis.mutate()}
            disabled={runProductionAnalysis.isPending}
            className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
          >
            {runProductionAnalysis.isPending ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Analyzing Production Plan...
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                Analyze Production Schedule
              </>
            )}
          </button>
        </CardContent>
      </Card>

      {/* Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <RecommendationCard
            result={result}
            agentType="production"
            onDismiss={() => setResult(null)}
          />
        </motion.div>
      )}

      {/* Production Lines Status - Real Data */}
      <Card>
        <CardHeader>
          <CardTitle>Production Lines Status - {productId}</CardTitle>
        </CardHeader>
        <CardContent>
          {productionLines.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No production lines assigned to {productId}
            </p>
          ) : (
            <div className="space-y-3">
              {productionLines.map((line) => (
                <ProductionLineRow key={line.id} line={line} />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Master Production Schedule - Real Data */}
      <Card>
        <CardHeader>
          <CardTitle>Master Production Schedule (MPS) - Next 4 Weeks</CardTitle>
        </CardHeader>
        <CardContent>
          {weeklySchedule.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No production schedule for {productId}
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Week</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Demand</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Planned</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Capacity</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Gap</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Overtime</th>
                    <th className="text-center py-3 px-4 font-semibold text-gray-700">Edit</th>
                  </tr>
                </thead>
                <tbody>
                  {weeklySchedule.map((week, idx) => (
                    <tr key={week.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium text-gray-900">Week {week.week_number}</td>
                      <td className="py-3 px-4 text-right text-gray-900">{formatNumber(week.demand)}</td>
                      <td className="py-3 px-4 text-right text-gray-900">{formatNumber(week.planned_production)}</td>
                      <td className="py-3 px-4 text-right text-gray-900">{formatNumber(week.capacity)}</td>
                      <td className={`py-3 px-4 text-right font-semibold ${week.gap < 0 ? 'text-red-600' : 'text-green-600'
                        }`}>
                        {week.gap > 0 ? '+' : ''}{formatNumber(week.gap)}
                      </td>
                      <td className="py-3 px-4 text-right">
                        {week.overtime_hours === 0 ? (
                          <Badge variant="success">No</Badge>
                        ) : (
                          <Badge variant="warning">{Math.round(week.overtime_hours)}h</Badge>
                        )}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <button
                          onClick={() => handleEditSchedule(week)}
                          className="p-1 hover:bg-gray-100 rounded"
                        >
                          <Edit className="h-4 w-4 text-gray-600" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Capacity Analysis - Dynamic */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Factory className="h-5 w-5 text-blue-600" />
              Capacity Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <InfoRow label="Weekly Capacity" value={`${formatNumber(weeklyCapacity)} units`} />
              <InfoRow label="Operational Lines" value={`${operationalLines.length} / ${productionLines.length}`} />
              <InfoRow
                label="Avg Utilization"
                value={`${avgUtilization}%`}
                status={avgUtilization >= 75 ? 'good' : 'warning'}
              />
              <InfoRow
                label="Capacity Loss"
                value={`${formatNumber(totalCapacityLoss)} units/week`}
                status={totalCapacityLoss > 0 ? 'warning' : 'good'}
              />
              {totalCapacityLoss > 0 && (
                <div className="pt-3 border-t border-gray-200">
                  <p className="text-sm text-gray-600">
                    {productionLines.filter(l => l.status === 'maintenance').length} line(s) under maintenance
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Bottleneck Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {productionLines
                .filter(l => l.bottleneck_machine_id || l.status === 'maintenance')
                .map((line, idx) => (
                  <BottleneckItem
                    key={line.id}
                    machine={line.bottleneck_machine_id || line.name}
                    line={line.name}
                    impact={line.status === 'maintenance' ? '100% line down' : `${100 - line.utilization}% capacity loss`}
                    status={line.status === 'maintenance' ? 'maintenance' : line.utilization < 70 ? 'critical' : 'active'}
                  />
                ))}
              {productionLines.filter(l => l.bottleneck_machine_id || l.status === 'maintenance').length === 0 && (
                <p className="text-sm text-green-600 text-center py-4">
                  ✓ No bottlenecks detected - all lines running optimally
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommendations - Dynamic based on data */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Recommendations
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            {totalOvertimeHours > 0 && (
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span>Schedule {Math.round(totalOvertimeHours)} hours of overtime over next 4 weeks to meet demand</span>
              </li>
            )}
            {uniqueBottlenecks.length > 0 && (
              <li className="flex items-start gap-2">
                <span className="text-orange-600 mt-1">⚠</span>
                <span>Address bottlenecks: {uniqueBottlenecks.join(', ')} - potential capacity unlock</span>
              </li>
            )}
            {productionLines.filter(l => l.status === 'maintenance').length > 0 && (
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span>
                  {productionLines.filter(l => l.status === 'maintenance').map(l => l.name).join(', ')} under maintenance -
                  will restore {formatNumber(totalCapacityLoss)} units/week capacity when complete
                </span>
              </li>
            )}
            {avgUtilization >= 85 && (
              <li className="flex items-start gap-2">
                <span className="text-blue-600 mt-1">✓</span>
                <span>High utilization ({avgUtilization}%) - consider adding capacity for growth</span>
              </li>
            )}
            {weeklySchedule.filter(w => w.gap < 0).length > 0 && (
              <li className="flex items-start gap-2">
                <span className="text-orange-600 mt-1">⚠</span>
                <span>
                  Capacity gaps detected in {weeklySchedule.filter(w => w.gap < 0).length} week(s) -
                  total shortfall: {formatNumber(Math.abs(weeklySchedule.reduce((sum, w) => sum + Math.min(w.gap, 0), 0)))} units
                </span>
              </li>
            )}
          </ul>
        </CardContent>
      </Card>

      <ScheduleEditModal
        isOpen={showEditModal}
        onClose={() => setShowEditModal(false)}
        onSave={handleSaveSchedule}
        scheduleRow={selectedRow}
        currentUser={currentUser}
      />
    </div>
  )
}

function MetricCard({ icon: Icon, title, value, subtitle, color }) {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600',
    red: 'bg-red-50 text-red-600',
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className={`p-2 rounded-lg ${colorMap[color]} w-fit mb-3`}>
          <Icon className="h-5 w-5" />
        </div>
        <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
      </CardContent>
    </Card>
  )
}

function ProductionLineRow({ line }) {
  const statusConfig = {
    running: { badge: 'success', color: 'text-green-600' },
    maintenance: { badge: 'error', color: 'text-red-600' },
  }

  const config = statusConfig[line.status] || statusConfig.running

  return (
    <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-all">
      <div className="flex items-center gap-4 flex-1">
        <Factory className={`h-5 w-5 ${config.color}`} />
        <div>
          <p className="font-medium text-gray-900">{line.name}</p>
          <p className="text-sm text-gray-500">Product: {line.product_name || 'Not assigned'}</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <p className="text-sm text-gray-600">Capacity</p>
          <p className="font-semibold text-gray-900">{line.capacity_per_hour}/hr</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">Utilization</p>
          <p className={`font-semibold ${line.utilization === 0 ? 'text-red-600' :
              line.utilization > 85 ? 'text-green-600' :
                'text-yellow-600'
            }`}>
            {Math.round(line.utilization)}%
          </p>
        </div>
        <div className="text-right min-w-[100px]">
          <p className="text-sm text-gray-600">Bottleneck</p>
          <p className="text-xs text-gray-700">{line.bottleneck_machine_name || 'None'}</p>
        </div>
        <Badge variant={config.badge} className="uppercase">
          {line.status}
        </Badge>
      </div>
    </div>
  )
}

function InfoRow({ label, value, status }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-sm text-gray-600">{label}</span>
      <span className={`text-sm font-medium ${status === 'good' ? 'text-green-600' :
          status === 'warning' ? 'text-orange-600' :
            'text-gray-900'
        }`}>
        {value}
      </span>
    </div>
  )
}

function BottleneckItem({ machine, line, impact, status }) {
  const statusConfig = {
    active: { color: 'yellow', label: 'Active' },
    critical: { color: 'red', label: 'Critical' },
    maintenance: { color: 'blue', label: 'Maintenance' },
  }

  const config = statusConfig[status] || statusConfig.active

  return (
    <div className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex-1">
        <p className="font-medium text-gray-900">{machine}</p>
        <p className="text-sm text-gray-600 mt-1">{line} • {impact}</p>
      </div>
      <Badge variant={config.color === 'blue' ? 'info' : config.color === 'red' ? 'error' : 'warning'}>
        {config.label}
      </Badge>
    </div>
  )
}
