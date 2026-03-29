import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Cog, AlertTriangle, Activity, Wrench, Play, Loader2, CheckCircle, Download, Filter } from 'lucide-react'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import ProductSelector from '../components/ProductSelector'
import DateRangePicker from '../components/DateRangePicker'
import MachineDetailModal from '../components/MachineDetailModal'
import WorkOrderModal from '../components/WorkOrderModal'
import ExportButton from '../components/ExportButton'
import RecommendationCard from '../components/RecommendationCard'
import { apiClient } from '../lib/api'

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
          <h1 className="text-3xl font-bold text-gray-900">Machine Health</h1>
          <p className="mt-1 text-sm text-gray-500">
            Fleet monitoring, predictive maintenance, and OEE analysis
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center gap-2"
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
            <p className="text-sm text-gray-500">Click any machine for detailed view</p>
          </div>
        </CardHeader>
        <CardContent>
          {machinesLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            </div>
          ) : productMachines.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
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

      {/* Critical Alerts */}
      {productMachines.some(m => m.alarms && m.alarms.length > 0) && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-900">
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
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    orange: 'bg-orange-50 text-orange-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
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

function MachineRow({ machine, onClick, onCreateWorkOrder }) {
  const statusConfig = {
    healthy: { badge: 'success', color: 'text-green-600' },
    at_risk: { badge: 'warning', color: 'text-yellow-600' },
    critical: { badge: 'error', color: 'text-red-600' },
  }

  const config = statusConfig[machine.status]

  return (
    <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:shadow-md transition-all cursor-pointer group">
      <div className="flex items-center gap-4 flex-1" onClick={onClick}>
        <Cog className={`h-5 w-5 ${config.color} group-hover:scale-110 transition-transform`} />
        <div>
          <p className="font-medium text-gray-900 group-hover:text-primary-600 transition-colors">{machine.name}</p>
          <p className="text-sm text-gray-500">{machine.id} • {machine.line}</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-right" onClick={onClick}>
          <p className="text-sm text-gray-600">OEE</p>
          <p className={`text-lg font-semibold ${machine.oee >= 85 ? 'text-green-600' :
              machine.oee >= 70 ? 'text-yellow-600' :
                'text-red-600'
            }`}>
            {machine.oee}%
          </p>
        </div>
        <div className="text-right" onClick={onClick}>
          <p className="text-sm text-gray-600">Failure Risk</p>
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
          className="px-3 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center gap-2 opacity-0 group-hover:opacity-100"
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
      className={`p-3 rounded-lg border-l-4 cursor-pointer hover:shadow-md transition-all ${alarm.severity === 'critical' ? 'bg-red-50 border-red-500' :
          alarm.severity === 'high' ? 'bg-orange-50 border-orange-500' :
            alarm.severity === 'medium' ? 'bg-yellow-50 border-yellow-500' :
              'bg-blue-50 border-blue-500'
        }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-900">{machine.name}</span>
            <Badge variant={
              alarm.severity === 'critical' ? 'error' :
                alarm.severity === 'high' ? 'warning' :
                  'info'
            }>
              {alarm.severity.toUpperCase()}
            </Badge>
          </div>
          <p className="text-sm text-gray-700 mt-1">{alarm.message}</p>
          <p className="text-xs text-gray-600 mt-1">{alarm.time}</p>
        </div>
      </div>
    </div>
  )
}
