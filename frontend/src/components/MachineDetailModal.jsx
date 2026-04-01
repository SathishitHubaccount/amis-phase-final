import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Wrench, TrendingUp, AlertTriangle, Package, Clock, User, Loader2 } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import Modal from './Modal'
import Badge from './Badge'
import WorkOrderModal from './WorkOrderModal'
import { apiClient } from '../lib/api'

function generateMockOEEHistory(machine) {
  const today = new Date()
  const baseOEE = machine.oee ?? 80
  const baseAvail = machine.availability ?? 90
  const basePerf = machine.performance ?? 88
  const baseQuality = machine.quality ?? 97
  return Array.from({ length: 30 }, (_, i) => {
    const date = new Date(today)
    date.setDate(today.getDate() - (29 - i))
    const jitter = () => (Math.random() - 0.5) * 6
    return {
      date: date.toISOString().slice(0, 10),
      oee: Math.min(100, Math.max(50, Math.round((baseOEE + jitter()) * 10) / 10)),
      availability: Math.min(100, Math.max(60, Math.round((baseAvail + jitter()) * 10) / 10)),
      performance: Math.min(100, Math.max(60, Math.round((basePerf + jitter()) * 10) / 10)),
      quality: Math.min(100, Math.max(70, Math.round((baseQuality + jitter()) * 10) / 10)),
    }
  })
}

export default function MachineDetailModal({ isOpen, onClose, machine }) {
  const [showWorkOrder, setShowWorkOrder] = useState(false)

  // Fetch OEE history for trend chart
  const { data: oeeHistoryData, isLoading: oeeHistoryLoading } = useQuery({
    queryKey: ['oee-history', machine?.id],
    queryFn: async () => {
      try {
        const response = await apiClient.getMachineOEEHistory(machine.id, 30)
        return response.data.history
      } catch {
        return []
      }
    },
    enabled: !!machine?.id && isOpen,
  })

  // Fall back to generated mock data if API returns nothing
  const mockOEEHistory = useMemo(() => machine ? generateMockOEEHistory(machine) : [], [machine])
  const chartData = oeeHistoryData && oeeHistoryData.length > 0 ? oeeHistoryData : mockOEEHistory

  if (!machine) return null

  const getStatusColor = (status) => {
    if (status === 'healthy') return 'text-green-600 bg-green-50'
    if (status === 'at_risk') return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  const getStatusLabel = (status) => {
    if (status === 'healthy') return 'Healthy'
    if (status === 'at_risk') return 'At Risk'
    return 'Critical'
  }

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} title={`Machine Details: ${machine.id}`} size="lg">
        <div className="space-y-6">
          {/* Header Info */}
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-2xl font-bold text-white">{machine.name}</h3>
              <p className="text-sm text-slate-400 mt-1">
                {machine.type} • {machine.line}
              </p>
            </div>
            <div className={`px-4 py-2 rounded-lg font-semibold ${getStatusColor(machine.status)}`}>
              {getStatusLabel(machine.status)}
            </div>
          </div>

          {/* OEE Breakdown */}
          <div className="grid grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-600 font-medium">OEE</p>
              <p className="text-3xl font-bold text-blue-900 mt-1">{machine.oee}%</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-sm text-green-600 font-medium">Availability</p>
              <p className="text-3xl font-bold text-green-900 mt-1">{machine.availability}%</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <p className="text-sm text-purple-600 font-medium">Performance</p>
              <p className="text-3xl font-bold text-purple-900 mt-1">{machine.performance}%</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <p className="text-sm text-orange-600 font-medium">Quality</p>
              <p className="text-3xl font-bold text-orange-900 mt-1">{machine.quality}%</p>
            </div>
          </div>

          {/* 30-Day OEE Trend */}
          <div>
            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              30-Day OEE Trend
            </h4>
            {oeeHistoryLoading ? (
              <div className="flex justify-center items-center py-12 bg-slate-800 rounded-lg">
                <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
              </div>
            ) : (
              <div className="h-72 bg-slate-800 rounded-lg p-4">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorOEE" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorAvailability" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorPerformance" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorQuality" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis
                      dataKey="date"
                      stroke="#6b7280"
                      tick={{ fill: '#6b7280', fontSize: 11 }}
                      tickFormatter={(date) => {
                        const d = new Date(date)
                        return `${d.getMonth() + 1}/${d.getDate()}`
                      }}
                    />
                    <YAxis
                      stroke="#6b7280"
                      tick={{ fill: '#6b7280', fontSize: 11 }}
                      domain={[0, 100]}
                      label={{ value: 'Percentage (%)', angle: -90, position: 'insideLeft', fill: '#6b7280', fontSize: 12 }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                        padding: '12px',
                        fontSize: '12px',
                      }}
                      formatter={(value, name) => {
                        const labels = {
                          oee: 'OEE',
                          availability: 'Availability',
                          performance: 'Performance',
                          quality: 'Quality',
                        }
                        return [value + '%', labels[name] || name]
                      }}
                      labelFormatter={(date) => {
                        const d = new Date(date)
                        return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                      }}
                    />
                    <Legend
                      wrapperStyle={{ paddingTop: '10px', fontSize: '12px' }}
                      formatter={(value) => {
                        const labels = {
                          oee: 'Overall OEE',
                          availability: 'Availability',
                          performance: 'Performance',
                          quality: 'Quality',
                        }
                        return labels[value] || value
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="oee"
                      stroke="#3b82f6"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorOEE)"
                    />
                    <Area
                      type="monotone"
                      dataKey="availability"
                      stroke="#10b981"
                      strokeWidth={1.5}
                      fillOpacity={1}
                      fill="url(#colorAvailability)"
                    />
                    <Area
                      type="monotone"
                      dataKey="performance"
                      stroke="#8b5cf6"
                      strokeWidth={1.5}
                      fillOpacity={1}
                      fill="url(#colorPerformance)"
                    />
                    <Area
                      type="monotone"
                      dataKey="quality"
                      stroke="#f59e0b"
                      strokeWidth={1.5}
                      fillOpacity={1}
                      fill="url(#colorQuality)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Utilization & Risk */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 border border-slate-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                <h4 className="font-semibold text-white">Utilization</h4>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-white">{machine.currentUtilization ?? machine.current_utilization ?? '—'}%</span>
                <span className="text-sm text-slate-400">of {machine.productionCapacity ?? machine.production_capacity ?? '—'} units/day capacity</span>
              </div>
            </div>
            <div className="p-4 border border-slate-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className={`h-5 w-5 ${machine.failureRisk > 50 ? 'text-red-600' : machine.failureRisk > 25 ? 'text-yellow-600' : 'text-green-600'}`} />
                <h4 className="font-semibold text-white">Failure Risk</h4>
              </div>
              <div className="flex items-baseline gap-2">
                <span className={`text-2xl font-bold ${machine.failureRisk > 50 ? 'text-red-600' : machine.failureRisk > 25 ? 'text-yellow-600' : 'text-green-600'}`}>
                  {machine.failureRisk}%
                </span>
                <span className="text-sm text-slate-400">probability</span>
              </div>
            </div>
          </div>

          {/* Active Alarms */}
          {machine.alarms && machine.alarms.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                Active Alarms ({machine.alarms.length})
              </h4>
              <div className="space-y-2">
                {machine.alarms.map((alarm) => (
                  <div
                    key={alarm.id}
                    className={`p-3 rounded-lg border-l-4 ${
                      alarm.severity === 'critical' ? 'bg-red-50 border-red-500' :
                      alarm.severity === 'high' ? 'bg-orange-50 border-orange-500' :
                      alarm.severity === 'medium' ? 'bg-yellow-50 border-yellow-500' :
                      'bg-blue-50 border-blue-500'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-white">{alarm.message}</p>
                        <p className="text-xs text-slate-400 mt-1">{alarm.time}</p>
                      </div>
                      <Badge variant={
                        alarm.severity === 'critical' ? 'error' :
                        alarm.severity === 'high' ? 'warning' :
                        'info'
                      }>
                        {alarm.severity.toUpperCase()}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Maintenance Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-slate-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="h-5 w-5 text-slate-400" />
                <h5 className="font-semibold text-white">Last Maintenance</h5>
              </div>
              <p className="text-sm text-slate-300">{machine.lastMaintenance}</p>
            </div>
            <div className="p-4 bg-slate-800 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="h-5 w-5 text-slate-400" />
                <h5 className="font-semibold text-white">Next Scheduled</h5>
              </div>
              <p className="text-sm text-slate-300">{machine.nextMaintenance}</p>
            </div>
          </div>

          {/* Maintenance History */}
          {machine.maintenanceHistory && machine.maintenanceHistory.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                <Wrench className="h-5 w-5 text-blue-600" />
                Maintenance History
              </h4>
              <div className="space-y-2">
                {machine.maintenanceHistory.map((entry, idx) => (
                  <div key={idx} className="p-3 bg-slate-800 rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <Badge variant={entry.type === 'Preventive' ? 'success' : entry.type === 'Corrective' ? 'warning' : 'error'}>
                            {entry.type}
                          </Badge>
                          <span className="text-sm font-medium text-white">{entry.date}</span>
                        </div>
                        <p className="text-sm text-slate-300 mt-1">{entry.notes}</p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-slate-400">
                          <span className="flex items-center gap-1">
                            <User className="h-3 w-3" />
                            {entry.technician}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {entry.duration}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Spare Parts Inventory */}
          {machine.spareParts && machine.spareParts.length > 0 && (
            <div>
              <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                <Package className="h-5 w-5 text-purple-600" />
                Spare Parts Inventory
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-800">
                      <th className="text-left py-2 px-3 font-semibold text-slate-300">Part</th>
                      <th className="text-right py-2 px-3 font-semibold text-slate-300">Stock</th>
                      <th className="text-right py-2 px-3 font-semibold text-slate-300">Min Stock</th>
                      <th className="text-center py-2 px-3 font-semibold text-slate-300">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {machine.spareParts.map((part, idx) => (
                      <tr key={idx} className="border-b border-slate-800">
                        <td className="py-2 px-3 text-white">{part.part}</td>
                        <td className="py-2 px-3 text-right text-white">{part.stock}</td>
                        <td className="py-2 px-3 text-right text-white">{part.minStock}</td>
                        <td className="py-2 px-3 text-center">
                          <Badge variant={
                            part.status === 'CRITICAL' ? 'error' :
                            part.status === 'LOW' ? 'warning' :
                            'success'
                          }>
                            {part.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-slate-800">
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2.5 border border-slate-700 text-slate-300 rounded-lg font-medium hover:bg-slate-800 transition-colors"
            >
              Close
            </button>
            <button
              onClick={() => {
                onClose()
                setShowWorkOrder(true)
              }}
              className="flex-1 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 transition-all shadow-lg shadow-primary-500/30 flex items-center justify-center gap-2"
            >
              <Wrench className="h-5 w-5" />
              Create Work Order
            </button>
          </div>
        </div>
      </Modal>

      <WorkOrderModal
        isOpen={showWorkOrder}
        onClose={() => setShowWorkOrder(false)}
        machine={machine}
      />
    </>
  )
}
