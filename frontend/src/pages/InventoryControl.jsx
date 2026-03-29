import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Package, AlertTriangle, TrendingUp, DollarSign, Play, Loader2, ChevronDown, ChevronRight, Boxes, Settings } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import InventoryAdjustmentModal from '../components/InventoryAdjustmentModal'
import ExportButton from '../components/ExportButton'
import RecommendationCard from '../components/RecommendationCard'
import { apiClient } from '../lib/api'
import { formatNumber, formatCurrency } from '../lib/utils'

export default function InventoryControl() {
  const [productId, setProductId] = useState('PROD-A')
  const [result, setResult] = useState(null)
  const [showAdjustmentModal, setShowAdjustmentModal] = useState(false)

  // Fetch real inventory data from database
  const { data: inventoryData, isLoading: inventoryLoading } = useQuery({
    queryKey: ['inventory', productId],
    queryFn: async () => {
      const response = await apiClient.getProductInventory(productId)
      return response.data
    },
    enabled: !!productId,
  })

  // Fetch products for dropdown
  const { data: productsData } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await apiClient.getProducts()
      return response.data.products
    },
  })

  // Fetch inventory history for trend chart
  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['inventory-history', productId],
    queryFn: async () => {
      const response = await apiClient.getInventoryHistory(productId, 30)
      return response.data.history
    },
    enabled: !!productId,
  })

  // Fetch Bill of Materials (BOM)
  const { data: bomData, isLoading: bomLoading } = useQuery({
    queryKey: ['bom', productId],
    queryFn: async () => {
      const response = await apiClient.getProductBOM(productId)
      return response.data.bom
    },
    enabled: !!productId,
  })

  const runInventoryAnalysis = useMutation({
    mutationFn: (productId) => apiClient.runAgent('inventory',
      `Provide complete inventory analysis for ${productId} including current stock, reorder points, stockout risk, and replenishment schedule`,
      productId
    ),
    onSuccess: async (data) => {
      const runId = data.data.run_id
      // Poll for results
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

  // Calculate dynamic metrics
  const currentStock = inventoryData?.current_stock || 0
  const avgDailyUsage = inventoryData?.avg_daily_usage || 1
  const daysSupply = avgDailyUsage > 0 ? Math.round(currentStock / avgDailyUsage) : 0
  const reorderPoint = inventoryData?.reorder_point || 0
  const safetyStock = inventoryData?.safety_stock || 0
  const stockoutRisk = inventoryData?.stockout_risk || 0
  const daysUntilReorder = avgDailyUsage > 0 ? Math.round((currentStock - reorderPoint) / avgDailyUsage) : 0

  return (
    <div className="space-y-6">
      {/* Page Header with Product Selector */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Inventory Control</h1>
          <p className="mt-1 text-sm text-gray-500">
            Stock levels, reorder points, and stockout risk analysis
          </p>
        </div>
        <div className="flex gap-4 items-end">
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
          <div className="flex items-center gap-3">
            <ExportButton
              endpoint="/api/export/inventory"
              label="Export All Inventory"
            />
            <ExportButton
              endpoint={`/api/export/inventory/${productId}/history`}
              label="Export History"
            />
          </div>
          <button
            onClick={() => setShowAdjustmentModal(true)}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors flex items-center gap-2 shadow-md"
          >
            <Settings className="h-4 w-4" />
            Adjust Stock
          </button>
        </div>
      </div>

      {/* Quick Metrics */}
      {inventoryLoading ? (
        <div className="flex justify-center items-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <MetricCard
            icon={Package}
            title="Current Stock"
            value={`${formatNumber(currentStock)} units`}
            subtitle={`${daysSupply} days supply`}
            color="blue"
          />
          <MetricCard
            icon={AlertTriangle}
            title="Stockout Risk"
            value={`${stockoutRisk}%`}
            subtitle="Next 14 days"
            color={stockoutRisk > 10 ? "orange" : "yellow"}
          />
          <MetricCard
            icon={TrendingUp}
            title="Reorder Point"
            value={`${formatNumber(reorderPoint)} units`}
            subtitle={daysUntilReorder > 0 ? `${daysUntilReorder} days until ROP` : 'Below ROP!'}
            color="purple"
          />
          <MetricCard
            icon={DollarSign}
            title="Safety Stock"
            value={`${formatNumber(safetyStock)} units`}
            subtitle={currentStock > safetyStock ? 'Above safety stock' : 'Below safety stock!'}
            color={currentStock > safetyStock ? "green" : "orange"}
          />
        </div>
      )}

      {/* Analysis Tool */}
      <Card>
        <CardHeader>
          <CardTitle>Run Inventory Analysis</CardTitle>
          <CardDescription>
            Get AI-powered inventory recommendations with stockout risk simulation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Product ID
              </label>
              <input
                type="text"
                value={productId}
                onChange={(e) => setProductId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., PROD-A"
                disabled={runInventoryAnalysis.isPending}
              />
            </div>
            <button
              onClick={() => runInventoryAnalysis.mutate(productId)}
              disabled={runInventoryAnalysis.isPending || !productId}
              className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
            >
              {runInventoryAnalysis.isPending ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Play className="h-5 w-5" />
                  Analyze
                </>
              )}
            </button>
          </div>
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
            agentType="inventory"
            onDismiss={() => setResult(null)}
          />
        </motion.div>
      )}

      {/* 30-Day Inventory Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            30-Day Inventory Trend
          </CardTitle>
          <CardDescription>
            Historical stock levels and stockout risk for {productId}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {historyLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            </div>
          ) : !historyData || historyData.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No historical data available for {productId}
            </p>
          ) : (
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historyData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis
                    dataKey="date"
                    stroke="#6b7280"
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                    tickFormatter={(date) => {
                      const d = new Date(date)
                      return `${d.getMonth() + 1}/${d.getDate()}`
                    }}
                  />
                  <YAxis
                    yAxisId="left"
                    stroke="#3b82f6"
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                    label={{ value: 'Stock Level (units)', angle: -90, position: 'insideLeft', fill: '#3b82f6' }}
                  />
                  <YAxis
                    yAxisId="right"
                    orientation="right"
                    stroke="#ef4444"
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                    label={{ value: 'Stockout Risk (%)', angle: 90, position: 'insideRight', fill: '#ef4444' }}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                      padding: '12px',
                    }}
                    formatter={(value, name) => {
                      if (name === 'stock_level') return [formatNumber(value) + ' units', 'Stock Level']
                      if (name === 'stockout_risk') return [value + '%', 'Stockout Risk']
                      if (name === 'days_supply') return [value?.toFixed(1) + ' days', 'Days Supply']
                      return [value, name]
                    }}
                    labelFormatter={(date) => {
                      const d = new Date(date)
                      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                    }}
                  />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    formatter={(value) => {
                      if (value === 'stock_level') return 'Stock Level (units)'
                      if (value === 'stockout_risk') return 'Stockout Risk (%)'
                      if (value === 'days_supply') return 'Days Supply'
                      return value
                    }}
                  />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="stock_level"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', r: 3 }}
                    activeDot={{ r: 5 }}
                    name="stock_level"
                  />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="stockout_risk"
                    stroke="#ef4444"
                    strokeWidth={2}
                    dot={{ fill: '#ef4444', r: 3 }}
                    activeDot={{ r: 5 }}
                    name="stockout_risk"
                  />
                  <Line
                    yAxisId="left"
                    type="monotone"
                    dataKey="days_supply"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ fill: '#8b5cf6', r: 2 }}
                    name="days_supply"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Key Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5 text-blue-600" />
              Current Position
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <InfoRow label="Stock on Hand" value={`${formatNumber(currentStock)} units`} />
              <InfoRow label="Safety Stock" value={`${formatNumber(safetyStock)} units`} />
              <InfoRow label="Reorder Point" value={`${formatNumber(reorderPoint)} units`} />
              <InfoRow label="Days of Supply" value={`${daysSupply} days`} />
              <div className="pt-3 border-t border-gray-200">
                <Badge variant={currentStock > safetyStock ? "success" : "danger"}>
                  {currentStock > safetyStock ? 'Above Safety Stock' : 'Below Safety Stock'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
              Risk Assessment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <InfoRow
                label="14-Day Stockout Risk"
                value={`${stockoutRisk}%`}
                status={stockoutRisk < 5 ? "good" : stockoutRisk < 15 ? "warning" : "danger"}
              />
              <InfoRow label="Lead Time" value={`${inventoryData?.lead_time || 0} days`} />
              <InfoRow label="Avg Daily Usage" value={`${formatNumber(avgDailyUsage)} units`} />
              <InfoRow
                label="Days Until Reorder"
                value={daysUntilReorder > 0 ? `${daysUntilReorder} days` : 'Reorder Now!'}
                status={daysUntilReorder > 3 ? "good" : "warning"}
              />
              <div className="pt-3 border-t border-gray-200">
                <Badge variant={stockoutRisk < 10 ? "success" : "warning"}>
                  {stockoutRisk < 10 ? 'Low Risk' : 'Monitoring Required'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bill of Materials (BOM) */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Boxes className="h-5 w-5 text-purple-600" />
            Bill of Materials (BOM) - {productId}
          </CardTitle>
          <CardDescription>
            Component breakdown and inventory status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {bomLoading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
            </div>
          ) : !bomData || bomData.length === 0 ? (
            <p className="text-center text-gray-500 py-8">
              No BOM data available for {productId}
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b-2 border-gray-200 bg-gray-50">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Component</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Supplier</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Quantity Needed</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Current Stock</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Unit Cost</th>
                    <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {bomData.map((item, idx) => {
                    const stockStatus = item.current_stock >= item.quantity_needed * 2 ? 'good' :
                      item.current_stock >= item.quantity_needed ? 'warning' : 'danger'
                    return (
                      <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <Package className="h-4 w-4 text-gray-400" />
                            <span className="font-medium text-gray-900">{item.component_id}</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-gray-700">{item.supplier_name || 'N/A'}</td>
                        <td className="py-3 px-4 text-right font-medium text-gray-900">
                          {formatNumber(item.quantity_needed)}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <span className={`font-medium ${stockStatus === 'good' ? 'text-green-600' :
                              stockStatus === 'warning' ? 'text-yellow-600' :
                                'text-red-600'
                            }`}>
                            {formatNumber(item.current_stock)}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right text-gray-700">
                          {formatCurrency(item.unit_cost || 0)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <Badge variant={
                            stockStatus === 'good' ? 'success' :
                              stockStatus === 'warning' ? 'warning' :
                                'error'
                          }>
                            {stockStatus === 'good' ? 'ADEQUATE' :
                              stockStatus === 'warning' ? 'LOW' : 'CRITICAL'}
                          </Badge>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 border-gray-200 bg-gray-50 font-semibold">
                    <td colSpan="4" className="py-3 px-4 text-right text-gray-700">
                      Total BOM Cost:
                    </td>
                    <td className="py-3 px-4 text-right text-gray-900">
                      {formatCurrency(
                        bomData.reduce((sum, item) => sum + (item.quantity_needed * (item.unit_cost || 0)), 0)
                      )}
                    </td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            💡 AI Recommendations
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Current inventory position is adequate with 18.7 effective days of supply</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Increase safety stock from 300 to 596 units (saves $26,419 annually)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600 mt-1">✓</span>
              <span>Order 7,500 units over next 4 weeks ($383,500 total investment)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-yellow-600 mt-1">⚠</span>
              <span>Monitor stockout risk closely - reaches 41.5% by day 14 without action</span>
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Inventory Adjustment Modal */}
      <InventoryAdjustmentModal
        isOpen={showAdjustmentModal}
        onClose={() => setShowAdjustmentModal(false)}
        productId={productId}
        productName={productsData?.find(p => p.id === productId)?.name || productId}
        currentStock={currentStock}
      />
    </div>
  )
}

function MetricCard({ icon: Icon, title, value, subtitle, color }) {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
    green: 'bg-green-50 text-green-600',
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

function InfoRow({ label, value, status }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-sm text-gray-600">{label}</span>
      <span className={`text-sm font-medium ${status === 'good' ? 'text-green-600' :
          status === 'warning' ? 'text-yellow-600' :
            status === 'danger' ? 'text-red-600' :
              'text-gray-900'
        }`}>
        {value}
      </span>
    </div>
  )
}
