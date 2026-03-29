import { useState, useEffect } from 'react'
import {
  Factory,
  Cpu,
  Radio,
  Database,
  AlertTriangle,
  TrendingUp,
  CheckCircle,
  RefreshCw,
} from 'lucide-react'
import Card, { CardHeader, CardTitle, CardContent } from '../components/Card'
import Badge from '../components/Badge'

const integrations = [
  {
    id: 'sap',
    icon: Factory,
    name: 'SAP S/4HANA ERP',
    status: 'connected',
    description: 'Production orders, BOM, master data',
    lastSync: '2 min ago',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
  },
  {
    id: 'mes',
    icon: Cpu,
    name: 'Siemens MES',
    status: 'connected',
    description: 'Real-time OEE, downtime events, production data',
    lastSync: '1 min ago',
    color: 'text-green-600',
    bgColor: 'bg-green-50',
  },
  {
    id: 'mqtt',
    icon: Radio,
    name: 'MQTT Broker',
    status: 'streaming',
    description: '47 IoT devices, 2.4K msgs/sec',
    lastSync: 'Live',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
  },
  {
    id: 'historian',
    icon: Database,
    name: 'OSIsoft PI Historian',
    status: 'connected',
    description: 'Time-series sensor history, 2M points/day',
    lastSync: '5 min ago',
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
  },
  {
    id: 'sftp',
    icon: AlertTriangle,
    name: 'SFTP File Exchange',
    status: 'warning',
    description: 'Expected hourly — last file 6h ago',
    lastSync: '6 hours ago',
    color: 'text-yellow-600',
    bgColor: 'bg-yellow-50',
  },
  {
    id: 'erp_demand',
    icon: TrendingUp,
    name: 'ERP Demand Module',
    status: 'connected',
    description: 'Customer orders, demand forecasts',
    lastSync: '15 min ago',
    color: 'text-teal-600',
    bgColor: 'bg-teal-50',
  },
]

const initialEvents = [
  { timestamp: '10:42:15', system: 'SAP S/4HANA ERP', event: 'Production order sync', records: 24, status: 'success' },
  { timestamp: '10:42:08', system: 'Siemens MES', event: 'OEE data push', records: 6, status: 'success' },
  { timestamp: '10:42:01', system: 'MQTT Broker', event: 'Sensor telemetry batch', records: 2400, status: 'success' },
  { timestamp: '10:41:55', system: 'OSIsoft PI Historian', event: 'Time-series write', records: 1800, status: 'success' },
  { timestamp: '10:41:48', system: 'ERP Demand Module', event: 'Forecast update', records: 12, status: 'success' },
  { timestamp: '10:41:40', system: 'SAP S/4HANA ERP', event: 'BOM master data sync', records: 3, status: 'success' },
  { timestamp: '10:41:32', system: 'Siemens MES', event: 'Downtime event logged', records: 1, status: 'success' },
  { timestamp: '10:40:55', system: 'SFTP File Exchange', event: 'File poll — no new file', records: 0, status: 'warning' },
]

const eventPool = [
  { system: 'SAP S/4HANA ERP', event: 'Production order sync', records: 18 },
  { system: 'Siemens MES', event: 'OEE data push', records: 6 },
  { system: 'MQTT Broker', event: 'Sensor telemetry batch', records: 2400 },
  { system: 'OSIsoft PI Historian', event: 'Time-series write', records: 1600 },
  { system: 'ERP Demand Module', event: 'Demand forecast refresh', records: 8 },
  { system: 'SAP S/4HANA ERP', event: 'Inventory adjustment', records: 2 },
  { system: 'Siemens MES', event: 'Shift report sync', records: 1 },
]

function formatTime(date) {
  return date.toTimeString().split(' ')[0]
}

export default function Integrations() {
  const [events, setEvents] = useState(initialEvents)
  const [lastSyncTime, setLastSyncTime] = useState(new Date())

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date()
      setLastSyncTime(now)
      const randomEvent = eventPool[Math.floor(Math.random() * eventPool.length)]
      const newEvent = {
        timestamp: formatTime(now),
        system: randomEvent.system,
        event: randomEvent.event,
        records: randomEvent.records,
        status: 'success',
      }
      setEvents((prev) => [newEvent, ...prev.slice(0, 14)])
    }, 10000)

    return () => clearInterval(interval)
  }, [])

  const connectedCount = integrations.filter(
    (i) => i.status === 'connected' || i.status === 'streaming'
  ).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Integration Hub</h1>
        <p className="mt-1 text-sm text-gray-500">
          Real-time connectivity with enterprise systems and IoT infrastructure
        </p>
      </div>

      {/* System Status Bar */}
      <div className="flex items-center justify-between p-4 bg-green-50 rounded-xl border border-green-200">
        <div className="flex items-center gap-3">
          <div className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />
          <span className="text-sm font-semibold text-green-800">
            {connectedCount}/{integrations.length} Systems Connected
          </span>
          {connectedCount < integrations.length && (
            <Badge variant="warning">
              {integrations.length - connectedCount} warning
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <RefreshCw className="h-3.5 w-3.5" />
          Last sync: {lastSyncTime.toLocaleTimeString()}
        </div>
      </div>

      {/* Integration Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {integrations.map((integration) => {
          const Icon = integration.icon
          return (
            <Card key={integration.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-2.5 rounded-lg ${integration.bgColor}`}>
                    <Icon className={`h-5 w-5 ${integration.color}`} />
                  </div>
                  {integration.status === 'connected' && (
                    <Badge variant="success">Connected</Badge>
                  )}
                  {integration.status === 'streaming' && (
                    <span className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-100 text-green-800">
                      <span className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                      Streaming
                    </span>
                  )}
                  {integration.status === 'warning' && (
                    <Badge variant="warning">Warning</Badge>
                  )}
                </div>
                <h3 className="font-semibold text-gray-900 mb-1">{integration.name}</h3>
                <p className="text-sm text-gray-500 mb-3">{integration.description}</p>
                <div className="flex items-center gap-2 text-xs text-gray-400">
                  <RefreshCw className="h-3 w-3" />
                  <span>Last sync: {integration.lastSync}</span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Live Sync Event Log */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
            Live Data Stream
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="text-left py-2.5 px-4 font-semibold text-gray-700">Timestamp</th>
                  <th className="text-left py-2.5 px-4 font-semibold text-gray-700">System</th>
                  <th className="text-left py-2.5 px-4 font-semibold text-gray-700">Event</th>
                  <th className="text-right py-2.5 px-4 font-semibold text-gray-700">Records</th>
                  <th className="text-center py-2.5 px-4 font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {events.map((event, idx) => (
                  <tr key={idx} className={`border-b border-gray-100 hover:bg-gray-50 ${idx === 0 ? 'bg-blue-50' : ''}`}>
                    <td className="py-2.5 px-4 font-mono text-xs text-gray-600">{event.timestamp}</td>
                    <td className="py-2.5 px-4 text-gray-800 font-medium">{event.system}</td>
                    <td className="py-2.5 px-4 text-gray-600">{event.event}</td>
                    <td className="py-2.5 px-4 text-right text-gray-800">{event.records.toLocaleString()}</td>
                    <td className="py-2.5 px-4 text-center">
                      {event.status === 'success' ? (
                        <Badge variant="success">OK</Badge>
                      ) : (
                        <Badge variant="warning">Warn</Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* ISA-95 Note */}
      <div className="p-4 bg-blue-50 rounded-xl border border-blue-200">
        <p className="text-xs text-blue-700">
          <strong>ISA-95 Compliance:</strong> All integrations follow ISA-95 Level 3 (MES) and Level 4 (ERP) interchange standards.
          Data flows are logged for audit and comply with IEC 62443 industrial cybersecurity guidelines.
        </p>
      </div>
    </div>
  )
}
