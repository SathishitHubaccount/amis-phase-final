import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Truck, TrendingUp, AlertTriangle, DollarSign, Play, Loader2, CheckCircle, Star } from 'lucide-react'
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Label } from 'recharts'
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
          <h1 className="text-3xl font-bold text-white">Supplier Management</h1>
          <p className="mt-1 text-sm text-slate-500">
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
                <tr className="border-b border-slate-800">
                  <th className="text-left py-3 px-4 font-semibold text-slate-300">PO Number</th>
                  <th className="text-left py-3 px-4 font-semibold text-slate-300">Supplier</th>
                  <th className="text-right py-3 px-4 font-semibold text-slate-300">Quantity</th>
                  <th className="text-right py-3 px-4 font-semibold text-slate-300">Value</th>
                  <th className="text-right py-3 px-4 font-semibold text-slate-300">Delivery Date</th>
                  <th className="text-center py-3 px-4 font-semibold text-slate-300">Status</th>
                </tr>
              </thead>
              <tbody>
                {openOrders.map((order) => (
                  <tr key={order.po} className="border-b border-slate-800 hover:bg-slate-800">
                    <td className="py-3 px-4 font-medium text-white">{order.po}</td>
                    <td className="py-3 px-4 text-white">{order.supplier}</td>
                    <td className="py-3 px-4 text-right text-white">{order.quantity.toLocaleString()} units</td>
                    <td className="py-3 px-4 text-right text-white">{order.value}</td>
                    <td className="py-3 px-4 text-right text-white">{order.deliveryDate}</td>
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

      {/* Supplier Risk Matrix (Scatter Chart) */}
      {suppliers.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              Supplier Risk Matrix
            </CardTitle>
            <CardDescription>Performance score vs on-time delivery — bubble size = quality score</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 30, bottom: 30, left: 30 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis type="number" dataKey="x" name="Performance" domain={[60, 100]} tick={{ fontSize: 11 }}>
                    <Label value="Performance Score" offset={-10} position="insideBottom" style={{ fontSize: 11, fill: '#6b7280' }} />
                  </XAxis>
                  <YAxis type="number" dataKey="y" name="On-Time %" domain={[60, 100]} tick={{ fontSize: 11 }}>
                    <Label value="On-Time Delivery %" angle={-90} position="insideLeft" style={{ fontSize: 11, fill: '#6b7280' }} />
                  </YAxis>
                  <ZAxis type="number" dataKey="z" range={[80, 400]} />
                  <ReferenceLine x={80} stroke="#9ca3af" strokeDasharray="4 4" label={{ value: 'Min Score', position: 'top', fontSize: 10, fill: '#9ca3af' }} />
                  <ReferenceLine y={85} stroke="#9ca3af" strokeDasharray="4 4" label={{ value: 'Min OTD', position: 'right', fontSize: 10, fill: '#9ca3af' }} />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    content={({ payload }) => {
                      if (!payload?.length) return null
                      const d = payload[0].payload
                      return (
                        <div className="bg-slate-800 border border-slate-700 rounded-lg p-3 shadow-lg text-xs">
                          <p className="font-semibold text-white mb-1">{d.name}</p>
                          <p className="text-slate-400">Performance: <span className="font-medium text-white">{d.x}/100</span></p>
                          <p className="text-slate-400">On-Time: <span className="font-medium text-white">{d.y}%</span></p>
                          <p className="text-slate-400">Quality: <span className="font-medium text-white">{d.z}%</span></p>
                          <p className="text-slate-400">Rating: <span className="font-medium text-white">{d.rating}</span></p>
                        </div>
                      )
                    }}
                  />
                  <Scatter
                    data={suppliers.map((s, i) => ({
                      x: s.score || s.performance_score || 0,
                      y: s.on_time_delivery || 0,
                      z: s.quality_score || s.quality_rating || 80,
                      name: s.name,
                      rating: s.rating,
                    }))}
                    fill="#3b82f6"
                    fillOpacity={0.75}
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-slate-500 text-center mt-1">Suppliers in the top-right quadrant (high score + high OTD) are preferred partners</p>
          </CardContent>
        </Card>
      )}

      {/* Performance & Risk Analysis — real data from DB */}
      {suppliers.length > 0 && (() => {
        const sorted = [...suppliers].sort((a, b) =>
          (b.score || b.performance_score || 0) - (a.score || a.performance_score || 0)
        )
        const top = sorted[0]
        const riskSuppliers = suppliers.filter(s => {
          const r = (s.risk || s.risk_status || '').toLowerCase()
          return r === 'high' || r === 'medium'
        }).sort((a, b) => {
          const order = { high: 0, medium: 1 }
          return (order[(a.risk || a.risk_status || '').toLowerCase()] ?? 2) -
                 (order[(b.risk || b.risk_status || '').toLowerCase()] ?? 2)
        })

        // Compute PO allocation from real purchase orders
        const totalQty = openOrders.reduce((s, o) => s + (o.quantity || 0), 0)
        const bySupplier = {}
        openOrders.forEach(o => {
          bySupplier[o.supplier] = (bySupplier[o.supplier] || 0) + (o.quantity || 0)
        })
        const allocations = Object.entries(bySupplier)
          .map(([name, qty]) => ({ name, pct: totalQty > 0 ? Math.round((qty / totalQty) * 100) : 0 }))
          .sort((a, b) => b.pct - a.pct)

        // Recommended = boost the top performer, reduce any high-risk supplier
        const highRiskNames = new Set(
          suppliers.filter(s => (s.risk || s.risk_status || '').toLowerCase() === 'high').map(s => s.name)
        )
        const recommendedTop = sorted.slice(0, 2)

        return (
          <>
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
                    <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-emerald-500/10 rounded-lg">
                          <Star className="h-5 w-5 text-green-600" />
                        </div>
                        <div>
                          <p className="font-semibold text-white">{top.name}</p>
                          <p className="text-sm text-slate-500">{top.id} • Rating: {top.rating || 'N/A'}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-green-600">{top.score || top.performance_score || 0}</p>
                        <p className="text-xs text-slate-500">Overall Score</p>
                      </div>
                    </div>
                    <InfoRow label="On-Time Delivery" value={`${top.on_time_delivery || 0}%`} status={(top.on_time_delivery || 0) >= 90 ? 'good' : 'warning'} />
                    <InfoRow label="Quality Score" value={`${top.quality_score || top.quality_rating || 0}%`} status={(top.quality_score || top.quality_rating || 0) >= 90 ? 'good' : 'warning'} />
                    <InfoRow label="Cost per Unit" value={`$${top.base_cost || top.cost_per_unit || 0}`} />
                    <InfoRow label="Lead Time" value={`${top.lead_time || top.lead_time_days || 0} days`} status={(top.lead_time || top.lead_time_days || 999) <= 10 ? 'good' : 'warning'} />
                    <div className="pt-3 border-t border-slate-800">
                      <p className="text-sm text-emerald-400 bg-emerald-500/10 p-3 rounded-lg">
                        ✓ Recommended as primary supplier — highest score in your network
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
                    {riskSuppliers.length === 0 ? (
                      <p className="text-sm text-green-600 text-center py-4">✓ No high-risk suppliers detected</p>
                    ) : (
                      riskSuppliers.slice(0, 3).map(s => (
                        <RiskItem
                          key={s.id}
                          supplier={s.id}
                          name={s.name}
                          risk={`${(s.risk || s.risk_status)} Risk`}
                          reason={`${s.on_time_delivery || 0}% on-time delivery • Quality: ${s.quality_score || s.quality_rating || 0}%`}
                          status={(s.risk || s.risk_status || '').toLowerCase()}
                        />
                      ))
                    )}
                    {riskSuppliers.length > 0 && (
                      <div className="pt-3 border-t border-slate-800">
                        <p className="text-xs text-orange-400 bg-orange-500/10 border border-orange-500/20 p-3 rounded-lg">
                          ⚠️ Consider reducing orders from high-risk suppliers and increasing allocation to {top.name}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Dual-Sourcing Strategy — computed from real PO data */}
            <Card className="border-violet-500/20 bg-violet-500/10">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-violet-300 mb-3 flex items-center gap-2">
                  <CheckCircle className="h-5 w-5" />
                  Dual-Sourcing Strategy
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-violet-400 mb-2">
                      Current Allocation {allocations.length === 0 ? '(no open POs)' : `(${openOrders.length} open POs)`}
                    </h4>
                    <div className="space-y-2 text-sm">
                      {allocations.length > 0 ? allocations.map(({ name, pct }) => (
                        <div key={name} className="flex justify-between">
                          <span className="text-violet-400 truncate mr-2">{name}</span>
                          <span className="font-semibold text-violet-300 shrink-0">{pct}%</span>
                        </div>
                      )) : (
                        <p className="text-violet-400 text-xs">No purchase orders to compute allocation</p>
                      )}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-semibold text-violet-400 mb-2">Recommended Allocation</h4>
                    <div className="space-y-2 text-sm">
                      {recommendedTop.map((s, i) => (
                        <div key={s.id} className="flex justify-between">
                          <span className="text-violet-400 truncate mr-2">{s.name}</span>
                          <span className="font-semibold text-green-600">{i === 0 ? '70%' : '30%'} ↑</span>
                        </div>
                      ))}
                      {suppliers.filter(s => !recommendedTop.find(r => r.id === s.id)).map(s => (
                        <div key={s.id} className="flex justify-between">
                          <span className="text-violet-400 truncate mr-2">{s.name}</span>
                          <span className={`font-semibold ${highRiskNames.has(s.name) ? 'text-red-600' : 'text-orange-600'}`}>
                            {highRiskNames.has(s.name) ? '0% ↓' : 'Monitor'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-violet-500/20">
                  <p className="text-sm text-violet-400">
                    💡 Concentrating on top-{Math.min(2, suppliers.length)} performers by score reduces delivery risk and improves quality consistency
                  </p>
                </div>
              </CardContent>
            </Card>
          </>
        )
      })()}

      {/* Recommendations */}
      <Card className="border-blue-500/20 bg-blue-500/10">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-blue-300 mb-3 flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            AI Recommendations
          </h3>
          <ul className="space-y-2 text-sm text-blue-200">
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
    blue: 'bg-blue-500/10 text-blue-400',
    green: 'bg-emerald-500/10 text-emerald-400',
    purple: 'bg-violet-500/10 text-violet-400',
    orange: 'bg-orange-500/10 text-orange-400',
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
    <div className="flex items-center justify-between p-4 border border-slate-800 rounded-lg hover:border-slate-700 transition-all">
      <div className="flex items-center gap-4 flex-1">
        <Truck className="h-5 w-5 text-blue-600" />
        <div>
          <p className="font-medium text-white">{supplier.name}</p>
          <p className="text-sm text-slate-500">{supplier.id} • Lead Time: {supplier.lead_time || supplier.lead_time_days} days</p>
        </div>
      </div>
      <div className="flex items-center gap-6">
        <div className="text-right">
          <p className="text-sm text-slate-400">Score</p>
          <p className="text-lg font-bold text-white">{supplier.score || supplier.performance_score || 0}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-400">On-Time</p>
          <p className="font-semibold text-white">{supplier.on_time_delivery || 0}%</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-400">Quality</p>
          <p className="font-semibold text-white">{supplier.quality_score || supplier.quality_rating || 0}%</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-400">Cost</p>
          <p className="font-semibold text-white">${supplier.base_cost || supplier.cost_per_unit || 0}</p>
        </div>
        <div className="text-right min-w-[80px]">
          <p className="text-sm text-slate-400">Risk</p>
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
      <span className="text-sm text-slate-400">{label}</span>
      <span className={`text-sm font-medium ${status === 'good' ? 'text-green-600' :
          status === 'warning' ? 'text-orange-600' :
            'text-white'
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
    <div className="flex items-start justify-between p-3 bg-slate-800 rounded-lg">
      <div className="flex-1">
        <p className="font-medium text-white">{name}</p>
        <p className="text-xs text-slate-500 mt-1">{supplier}</p>
        <p className="text-sm text-slate-400 mt-1">{reason}</p>
      </div>
      <Badge variant={config.color === 'red' ? 'error' : 'warning'}>
        {config.label}
      </Badge>
    </div>
  )
}
