import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Truck, TrendingUp, AlertTriangle, DollarSign, Play, Loader2, CheckCircle, Star } from 'lucide-react'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import ExportButton from '../components/ExportButton'
import RecommendationCard from '../components/RecommendationCard'
import { apiClient } from '../lib/api'
import { formatNumber } from '../lib/utils'

export default function SupplierManagement() {
  const [result, setResult] = useState(null)
  const [selectedSupplier, setSelectedSupplier] = useState(null)

  // Fetch suppliers from database
  const { data: suppliersData, isLoading: suppliersLoading } = useQuery({
    queryKey: ['suppliers'],
    queryFn: async () => {
      const response = await apiClient.getSuppliers()
      return response.data.suppliers
    },
  })

  // Fetch real purchase orders from database
  const { data: purchaseOrdersData } = useQuery({
    queryKey: ['purchase-orders'],
    queryFn: async () => {
      const response = await apiClient.getPurchaseOrders()
      return response.data.purchase_orders
    },
  })

  const runSupplierAnalysis = useMutation({
    mutationFn: () => apiClient.runAgent('supplier',
      'Provide complete supplier analysis including performance evaluation, risk assessment, delivery simulation, dual-sourcing recommendations, and purchase order optimization for PROD-A',
      'PROD-A'
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

  // Use suppliers from database
  const suppliers = suppliersData || []

  // Calculate metrics from suppliers
  const avgScore = suppliers.length > 0
    ? Math.round(suppliers.reduce((sum, s) => sum + (s.score || s.performance_score || 0), 0) / suppliers.length)
    : 0

  const openOrders = (purchaseOrdersData || []).map(po => ({
    po: po.po_id,
    supplier: po.supplier_name || po.supplier_id,
    quantity: po.quantity,
    value: `$${po.total_cost?.toLocaleString()}`,
    deliveryDate: po.expected_delivery_date,
    status: po.status === 'delivered' ? 'delivered' : po.status === 'in_transit' ? 'on_track' : 'at_risk',
    rawStatus: po.status,
  }))

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Supplier Management</h1>
          <p className="mt-1 text-sm text-gray-500">
            Supplier evaluation, procurement optimization, and delivery risk assessment
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ExportButton
            endpoint="/api/export/suppliers"
            label="Export Suppliers"
          />
          <ExportButton
            endpoint="/api/export/work-orders"
            label="Export Work Orders"
          />
        </div>
      </div>

      {/* Quick Metrics */}
      {suppliersLoading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <MetricCard
            icon={Truck}
            title="Active Suppliers"
            value={suppliers.length.toString()}
            subtitle="All regions covered"
            color="blue"
          />
          <MetricCard
            icon={TrendingUp}
            title="Avg Supplier Score"
            value={`${avgScore}/100`}
            subtitle={avgScore >= 80 ? 'Above industry avg' : 'Below industry avg'}
            color={avgScore >= 80 ? 'green' : 'orange'}
          />
          <MetricCard
            icon={DollarSign}
            title="Total Suppliers"
            value={suppliers.length.toString()}
            subtitle={`Rating: ${suppliers.length > 0 ? suppliers[0].rating : '-'}`}
            color="purple"
          />
          <MetricCard
            icon={CheckCircle}
            title="Quality Rating"
            value={suppliers.length > 0 ? `${suppliers[0].quality_score || suppliers[0].quality_rating}%` : '-'}
            subtitle="Top supplier"
            color="green"
          />
        </div>
      )}

      {/* Analysis Tool */}
      <Card>
        <CardHeader>
          <CardTitle>Run Supplier Analysis</CardTitle>
          <CardDescription>
            Get AI-powered supplier evaluation, risk assessment, and dual-sourcing recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <button
            onClick={() => runSupplierAnalysis.mutate()}
            disabled={runSupplierAnalysis.isPending}
            className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
          >
            {runSupplierAnalysis.isPending ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Analyzing Suppliers...
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                Analyze Supplier Network
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
            agentType="supplier"
            onDismiss={() => setResult(null)}
          />
        </motion.div>
      )}

      {/* Supplier Scorecards */}
      <Card>
        <CardHeader>
          <CardTitle>Supplier Scorecards</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {suppliers.map((supplier) => (
              <SupplierRow key={supplier.id} supplier={supplier} />
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Open Purchase Orders */}
      <Card>
        <CardHeader>
          <CardTitle>Open Purchase Orders</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">PO Number</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Supplier</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Quantity</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Value</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Delivery Date</th>
                  <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {openOrders.map((order) => (
                  <tr key={order.po} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium text-gray-900">{order.po}</td>
                    <td className="py-3 px-4 text-gray-900">{order.supplier}</td>
                    <td className="py-3 px-4 text-right text-gray-900">{order.quantity.toLocaleString()} units</td>
                    <td className="py-3 px-4 text-right text-gray-900">{order.value}</td>
                    <td className="py-3 px-4 text-right text-gray-900">{order.deliveryDate}</td>
                    <td className="py-3 px-4 text-center">
                      {order.status === 'delivered' ? (
                        <Badge variant="success">Delivered</Badge>
                      ) : order.status === 'on_track' ? (
                        <Badge variant="info">In Transit</Badge>
                      ) : (
                        <Badge variant="warning">At Risk</Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Performance & Risk Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              Top Performer Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between pb-3 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <Star className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">Global Parts Co.</p>
                    <p className="text-sm text-gray-500">SUP-001 • Rating: A</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-green-600">92</p>
                  <p className="text-xs text-gray-500">Overall Score</p>
                </div>
              </div>
              <InfoRow label="On-Time Delivery" value="96%" status="good" />
              <InfoRow label="Quality Score" value="98%" status="good" />
              <InfoRow label="Cost per Unit" value="$51.20" />
              <InfoRow label="Lead Time" value="7 days" status="good" />
              <div className="pt-3 border-t border-gray-200">
                <p className="text-sm text-green-700 bg-green-50 p-3 rounded-lg">
                  ✓ Recommended as primary supplier - excellent track record
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-600" />
              Risk Assessment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <RiskItem
                supplier="SUP-004"
                name="Quality Supplies LLC"
                risk="High Risk"
                reason="74% on-time delivery rate, below threshold"
                status="high"
              />
              <RiskItem
                supplier="SUP-002"
                name="Precision Manufacturing Ltd."
                risk="Medium Risk"
                reason="PO-2026-002 delayed by 3 days"
                status="medium"
              />
              <div className="pt-3 border-t border-gray-200">
                <p className="text-xs text-orange-700 bg-orange-50 p-3 rounded-lg">
                  ⚠️ Recommendation: Diversify from SUP-004, allocate 70% to SUP-001 and 30% to SUP-003
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Dual-Sourcing Strategy */}
      <Card className="border-purple-200 bg-purple-50">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-purple-900 mb-3 flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Dual-Sourcing Strategy
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-purple-800 mb-2">Current Allocation</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-purple-700">SUP-001 (Global Parts)</span>
                  <span className="font-semibold text-purple-900">45%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">SUP-002 (Precision Mfg)</span>
                  <span className="font-semibold text-purple-900">20%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">SUP-003 (Eastern Components)</span>
                  <span className="font-semibold text-purple-900">25%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">SUP-004 (Quality Supplies)</span>
                  <span className="font-semibold text-purple-900">10%</span>
                </div>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-purple-800 mb-2">Recommended Allocation</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-purple-700">SUP-001 (Global Parts)</span>
                  <span className="font-semibold text-green-600">70% ↑</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">SUP-003 (Eastern Components)</span>
                  <span className="font-semibold text-green-600">30% ↑</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">SUP-002 (Precision Mfg)</span>
                  <span className="font-semibold text-orange-600">0% ↓</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-700">SUP-004 (Quality Supplies)</span>
                  <span className="font-semibold text-red-600">0% ↓</span>
                </div>
              </div>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-purple-300">
            <p className="text-sm text-purple-800">
              💡 Expected savings: $12,800/year with improved delivery reliability (+8% on-time rate)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            AI Recommendations
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Place 70% of orders with SUP-001 (Global Parts) - highest reliability and quality</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Use SUP-003 (Eastern Components) for 30% - good backup with competitive pricing</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-orange-600 mt-1">⚠</span>
              <span>Phase out SUP-004 - high risk profile with 74% on-time delivery rate</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Monitor PO-2026-002 closely - supplier SUP-002 showing delivery delays</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Next PO: 7,500 units split 5,250 (SUP-001) + 2,250 (SUP-003) over 4 weeks</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

function MetricCard({ icon: Icon, title, value, subtitle, color }) {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
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

function SupplierRow({ supplier }) {
  const getRatingColor = (rating) => {
    if (rating === 'A') return 'success'
    if (rating?.startsWith('B')) return 'warning'
    return 'error'
  }

  const getRiskColor = (riskStatus) => {
    if (riskStatus === 'Low' || riskStatus === 'low') return 'text-green-600'
    if (riskStatus === 'Medium' || riskStatus === 'medium') return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-all">
      <div className="flex items-center gap-4 flex-1">
        <Truck className="h-5 w-5 text-blue-600" />
        <div>
          <p className="font-medium text-gray-900">{supplier.name}</p>
          <p className="text-sm text-gray-500">{supplier.id} • Lead Time: {supplier.lead_time || supplier.lead_time_days} days</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <p className="text-sm text-gray-600">Score</p>
          <p className="text-lg font-bold text-gray-900">{supplier.score || supplier.performance_score || 0}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">On-Time</p>
          <p className="font-semibold text-gray-900">{supplier.on_time_delivery || 0}%</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">Quality</p>
          <p className="font-semibold text-gray-900">{supplier.quality_score || supplier.quality_rating || 0}%</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">Cost</p>
          <p className="font-semibold text-gray-900">${supplier.base_cost || supplier.cost_per_unit || 0}</p>
        </div>
        <div className="text-right min-w-[80px]">
          <p className="text-sm text-gray-600">Risk</p>
          <p className={`font-semibold ${getRiskColor(supplier.risk || supplier.risk_status)}`}>{supplier.risk || supplier.risk_status || 'Unknown'}</p>
        </div>
        <Badge variant={getRatingColor(supplier.rating)}>
          {supplier.rating || 'N/A'}
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

function RiskItem({ supplier, name, risk, reason, status }) {
  const statusConfig = {
    high: { color: 'red', label: 'High Risk' },
    medium: { color: 'yellow', label: 'Medium Risk' },
  }

  const config = statusConfig[status]

  return (
    <div className="flex items-start justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex-1">
        <p className="font-medium text-gray-900">{name}</p>
        <p className="text-xs text-gray-500 mt-1">{supplier}</p>
        <p className="text-sm text-gray-600 mt-1">{reason}</p>
      </div>
      <Badge variant={config.color === 'red' ? 'error' : 'warning'}>
        {config.label}
      </Badge>
    </div>
  )
}
