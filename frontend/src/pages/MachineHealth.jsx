import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Cog, AlertTriangle, Activity, Wrench, Play, Loader2, CheckCircle, Download, Filter } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import ProductSelector from '../components/ProductSelector'
import DateRangePicker from '../components/DateRangePicker'
import MachineDetailModal from '../components/MachineDetailModal'
import WorkOrderModal from '../components/WorkOrderModal'
import ExportButton from '../components/ExportButton'
import RecommendationCard from '../components/RecommendationCard'
import { apiClient } from '../lib/api'

function OEEGauge({ value }) {
  const radius = 20
  const circumference = 2 * Math.PI * radius
  const offset = circumference * (1 - value / 100)
  const color = value >= 85 ? '#16a34a' : value >= 70 ? '#ca8a04' : '#dc2626'
  return (
    <div className="relative flex-shrink-0" style={{ width: 52, height: 52 }}>
      <svg width="52" height="52" className="transform -rotate-90">
        <circle cx="26" cy="26" r={radius} stroke="#1e293b" strokeWidth="6" fill="none" />
        <circle
          cx="26" cy="26" r={radius}
          stroke={color} strokeWidth="6" fill="none"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-xs font-bold leading-none" style={{ color }}>{value}%</span>
      </div>
    </div>
  )
}

export default function MachineHealth() {
  const [selectedProduct, setSelectedProduct] = useState('PROD-A')
  const [result, setResult] = useState(null)
  const [selectedMachine, setSelectedMachine] = useState(null)
  const [showMachineDetail, setShowMachineDetail] = useState(false)
  const [showWorkOrder, setShowWorkOrder] = useState(false)
  const [showFilters, setShowFilters] = useState(false)

  // Fetch machines from database
  const { data: machinesData, isLoading: machinesLoading } = useQuery({
    queryKey: ['machines', selectedProduct],
    queryFn: async () => {
      const response = await apiClient.getMachines(selectedProduct)
      return response.data.machines
    },
  })

  // Date range for historical trending
  const [startDate, setStartDate] = useState(() => {
    const date = new Date()
    date.setDate(date.getDate() - 30)
    return date.toISOString().split('T')[0]
  })
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])

  const runMachineAnalysis = useMutation({
    mutationFn: () => {
      return apiClient.runAgent('machine',
        `Provide complete machine health analysis for ${selectedProduct} including fleet status, failure predictions, OEE calculations, maintenance recommendations, and bottleneck identification. Time period: ${startDate} to ${endDate}`,
        selectedProduct
      )
    },
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

  const handleMachineClick = async (machineId) => {
    try {
      const response = await apiClient.getMachineDetail(machineId)
      setSelectedMachine(response.data)
      setShowMachineDetail(true)
    } catch (error) {
      console.error('Error fetching machine details:', error)
    }
  }

  const handleCreateWorkOrder = (machine) => {
    setSelectedMachine(machine)
    setShowWorkOrder(true)
  }

  const handleWorkOrderSubmit = async (workOrderData) => {
    try {
      const response = await apiClient.createWorkOrder(workOrderData)
      console.log('Work order created:', response.data)
      alert(`Work order ${response.data.work_order_id} created successfully!`)
      // Optionally refresh data or show success message
    } catch (error) {
      console.error('Error creating work order:', error)
      alert('Failed to create work order. Please try again.')
    }
  }

  const exportData = () => {
    alert('Export functionality would generate CSV/PDF report with machine data, OEE trends, and maintenance schedules')
  }

  // Use machines from database
  const productMachines = machinesData || []

  // Calculate metrics
  const totalMachines = productMachines.length
  const avgOEE = totalMachines > 0
    ? Math.round(productMachines.reduce((sum, m) => sum + m.oee, 0) / totalMachines)
    : 0
  const machinesAtRisk = productMachines.filter(m => m.status === 'at_risk' || m.status === 'critical').length
  const healthyLines = productMachines.filter(m => m.status === 'healthy').length

  return (
    <div className="space-y-6">
      {/* Page Header with Actions */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Machine Health</h1>
          <p className="mt-1 text-sm text-slate-400">
            Fleet monitoring, predictive maintenance, and OEE analysis
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 border border-slate-700 text-slate-300 rounded-lg font-medium hover:bg-slate-800 transition-colors flex items-center gap-2"
          >
            <Filter className="h-4 w-4" />
            {showFilters ? 'Hide' : 'Show'} Filters
          </button>
          <div className="flex items-center gap-3">
            <ExportButton
              endpoint="/api/export/machines"
              label="Export All Machines"
            />
          </div>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
        >
          <Card>
            <CardContent className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <ProductSelector
                  value={selectedProduct}
                  onChange={setSelectedProduct}
                />
                <DateRangePicker
                  startDate={startDate}
                  endDate={endDate}
                  onStartChange={setStartDate}
                  onEndChange={setEndDate}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Quick Metrics - Dynamic based on selected product */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard
          icon={Cog}
          title="Fleet OEE"
          value={`${avgOEE}%`}
          subtitle={avgOEE >= 85 ? 'Above target' : 'Below target (85%)'}
          color={avgOEE >= 85 ? 'green' : 'orange'}
        />
        <MetricCard
          icon={AlertTriangle}
          title="Machines at Risk"
          value={machinesAtRisk}
          subtitle={`out of ${totalMachines} machines`}
          color={machinesAtRisk > 0 ? 'red' : 'green'}
        />
        <MetricCard
          icon={Activity}
          title="Healthy Lines"
          value={`${healthyLines} / ${totalMachines}`}
          subtitle={totalMachines - healthyLines > 0 ? `${totalMachines - healthyLines} need attention` : 'All operational'}
          color={healthyLines === totalMachines ? 'green' : 'yellow'}
        />
        <MetricCard
          icon={Wrench}
          title="Maintenance Due"
          value={productMachines.filter(m => {
            const nextMaint = new Date(m.nextMaintenance)
            const today = new Date()
            const diffDays = (nextMaint - today) / (1000 * 60 * 60 * 24)
            return diffDays <= 7
          }).length}
          subtitle="Within 7 days"
          color="blue"
        />
      </div>

      {/* Analysis Tool */}
      <Card>
        <CardHeader>
          <CardTitle>Run Machine Health Analysis</CardTitle>
          <CardDescription>
            Get AI-powered predictive maintenance insights and failure risk assessment
          </CardDescription>
        </CardHeader>
        <CardContent>
          <button
            onClick={() => runMachineAnalysis.mutate()}
            disabled={runMachineAnalysis.isPending}
            className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
          >
            {runMachineAnalysis.isPending ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Analyzing Machines...
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                Analyze All Machines
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
            agentType="machine"
            onDismiss={() => setResult(null)}
          />
        </motion.div>
      )}

      {/* Fleet Status with Click to View Details */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Fleet Status - {selectedProduct}</CardTitle>
            <p className="text-sm text-slate-400">Click any machine for detailed view</p>
          </div>
        </CardHeader>
        <CardContent>
          {machinesLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            </div>
          ) : productMachines.length === 0 ? (
            <p className="text-center text-slate-400 py-8">
              No machines assigned to {selectedProduct}
            </p>
          ) : (
            <div className="space-y-3">
              {productMachines.map((machine) => (
                <MachineRow
                  key={machine.id}
                  machine={machine}
                  onClick={() => handleMachineClick(machine.id)}
                  onCreateWorkOrder={() => handleCreateWorkOrder(machine)}
                />
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Predictive Failure Risk Timeline */}
      {productMachines.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-red-500" />
              Predictive Failure Risk Timeline
            </CardTitle>
            <CardDescription>Current failure probability per machine — click a machine row above for 30-day OEE history</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  layout="vertical"
                  data={[...productMachines]
                    .sort((a, b) => b.failureRisk - a.failureRisk)
                    .map(m => ({ name: m.id, risk: m.failureRisk, label: m.name }))}
                  margin={{ top: 5, right: 40, left: 70, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} tickFormatter={v => `${v}%`} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={65} />
                  <Tooltip
                    formatter={(v, _, props) => [`${v}% failure risk`, props.payload.label]}
                    contentStyle={{ borderRadius: 8, fontSize: 12 }}
                  />
                  <Bar dataKey="risk" radius={[0, 6, 6, 0]} maxBarSize={28}>
                    {[...productMachines]
                      .sort((a, b) => b.failureRisk - a.failureRisk)
                      .map((m) => (
                        <Cell
                          key={m.id}
                          fill={m.failureRisk >= 50 ? '#dc2626' : m.failureRisk >= 20 ? '#f59e0b' : '#16a34a'}
                        />
                      ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="flex items-center gap-6 mt-3 justify-center text-xs text-slate-500">
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-green-600 inline-block" /> Low (&lt;20%)</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-amber-400 inline-block" /> Medium (20–50%)</span>
              <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-red-600 inline-block" /> High (&gt;50%)</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Critical Alerts */}
      {productMachines.some(m => m.alarms && m.alarms.length > 0) && (
        <Card className="border-orange-500/20 bg-orange-500/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-300">
              <AlertTriangle className="h-5 w-5" />
              Critical Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {productMachines
                .filter(m => m.alarms && m.alarms.length > 0)
                .map(machine =>
                  machine.alarms.map(alarm => (
                    <AlertItem
                      key={`${machine.id}-${alarm.id}`}
                      machine={machine}
                      alarm={alarm}
                      onClick={() => handleMachineClick(machine.id)}
                    />
                  ))
                )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Modals */}
      <MachineDetailModal
        isOpen={showMachineDetail}
        onClose={() => setShowMachineDetail(false)}
        machine={selectedMachine}
      />

      <WorkOrderModal
        isOpen={showWorkOrder}
        onClose={() => setShowWorkOrder(false)}
        onSubmit={handleWorkOrderSubmit}
        machines={productMachines}
        currentUser={JSON.parse(localStorage.getItem('user') || '{"username":"Admin"}')}
      />
    </div>
  )
}

function MetricCard({ icon: Icon, title, value, subtitle, color }) {
  const colorMap = {
    blue: 'bg-blue-500/10 text-blue-400',
    green: 'bg-emerald-500/10 text-emerald-400',
    orange: 'bg-orange-500/10 text-orange-400',
    red: 'bg-red-500/10 text-red-400',
    yellow: 'bg-amber-500/10 text-amber-400',
  }

  return (
    <Card>
      <CardContent className="p-6">
        <div className={`p-2 rounded-lg ${colorMap[color]} w-fit mb-3`}>
          <Icon className="h-5 w-5" />
        </div>
        <p className="text-sm font-medium text-slate-400 mb-1">{title}</p>
        <p className="text-2xl font-bold text-white">{value}</p>
        <p className="text-sm text-slate-500 mt-1">{subtitle}</p>
      </CardContent>
    </Card>
  )
}

function MachineRow({ machine, onClick, onCreateWorkOrder }) {
  const statusConfig = {
    healthy: { badge: 'success', color: 'text-green-600' },
    at_risk: { badge: 'warning', color: 'text-yellow-600' },
    critical: { badge: 'error', color: 'text-red-600' },
  }

  const config = statusConfig[machine.status]

  return (
    <div className="flex items-center justify-between p-4 border border-slate-800 rounded-lg hover:border-slate-600 hover:shadow-md transition-all cursor-pointer group">
      <div className="flex items-center gap-4 flex-1" onClick={onClick}>
        <Cog className={`h-5 w-5 ${config.color} group-hover:scale-110 transition-transform`} />
        <div>
          <p className="font-medium text-white group-hover:text-primary-400 transition-colors">{machine.name}</p>
          <p className="text-sm text-slate-500">{machine.id} • {machine.line}</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="flex flex-col items-center cursor-pointer" onClick={onClick}>
          <p className="text-xs text-slate-400 mb-1">OEE</p>
          <OEEGauge value={machine.oee} />
        </div>
        <div className="text-right" onClick={onClick}>
          <p className="text-sm text-slate-400">Failure Risk</p>
          <p className={`text-lg font-semibold ${machine.failureRisk < 20 ? 'text-green-600' :
              machine.failureRisk < 50 ? 'text-yellow-600' :
                'text-red-600'
            }`}>
            {machine.failureRisk}%
          </p>
        </div>
        <Badge variant={config.badge} className="uppercase min-w-[80px] text-center">
          {machine.status.replace('_', ' ')}
        </Badge>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onCreateWorkOrder()
          }}
          className="px-3 py-2 border border-slate-700 text-slate-300 rounded-lg text-sm font-medium hover:bg-slate-800 transition-colors flex items-center gap-2 opacity-0 group-hover:opacity-100"
        >
          <Wrench className="h-4 w-4" />
          Work Order
        </button>
      </div>
    </div>
  )
}

function AlertItem({ machine, alarm, onClick }) {
  return (
    <div
      onClick={onClick}
      className={`p-3 rounded-lg border-l-4 cursor-pointer hover:shadow-md transition-all ${alarm.severity === 'critical' ? 'bg-red-500/10 border-red-500/50' :
          alarm.severity === 'high' ? 'bg-orange-500/10 border-orange-500/50' :
            alarm.severity === 'medium' ? 'bg-amber-500/10 border-amber-500/50' :
              'bg-blue-500/10 border-blue-500/50'
        }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-white">{machine.name}</span>
            <Badge variant={
              alarm.severity === 'critical' ? 'error' :
                alarm.severity === 'high' ? 'warning' :
                  'info'
            }>
              {alarm.severity.toUpperCase()}
            </Badge>
          </div>
          <p className="text-sm text-slate-300 mt-1">{alarm.message}</p>
          <p className="text-xs text-slate-400 mt-1">{alarm.time}</p>
        </div>
      </div>
    </div>
  )
}
