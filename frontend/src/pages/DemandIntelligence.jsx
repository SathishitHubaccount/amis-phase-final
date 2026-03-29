import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { TrendingUp, AlertCircle, Play, Loader2, Plus } from 'lucide-react'
import { XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart, Line } from 'recharts'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import ForecastInputModal from '../components/ForecastInputModal'
import RecommendationCard from '../components/RecommendationCard'
import { apiClient } from '../lib/api'

export default function DemandIntelligence() {
  const [selectedProduct, setSelectedProduct] = useState('PROD-A')
  const [result, setResult] = useState(null)
  const [showForecastModal, setShowForecastModal] = useState(false)
  const [aiForeccastData, setAIForecastData] = useState(null)
  const [isImporting, setIsImporting] = useState(false)

  // Fetch product list with real names
  const { data: productsData } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await apiClient.getProducts()
      return response.data.products || response.data || []
    }
  })

  const products = productsData || []
  const selectedProductInfo = products.find(p => p.id === selectedProduct) || { id: selectedProduct, name: selectedProduct }

  // Fetch REAL forecast data from database
  const { data: forecastsData, isLoading, refetch } = useQuery({
    queryKey: ['demand-forecasts', selectedProduct],
    queryFn: async () => {
      const response = await apiClient.getDemandForecasts(selectedProduct, 12)
      return response.data.forecasts
    }
  })

  const forecastData = forecastsData || []

  // Calculate real insights from data
  const calculateInsights = () => {
    if (forecastData.length === 0) return null

    const avgBase = forecastData.reduce((sum, f) => sum + (f.base_case || 0), 0) / forecastData.length
    const avgOptimistic = forecastData.reduce((sum, f) => sum + (f.optimistic || 0), 0) / forecastData.length
    const avgPessimistic = forecastData.reduce((sum, f) => sum + (f.pessimistic || 0), 0) / forecastData.length

    // Calculate trend (simple linear regression slope)
    const trend = forecastData.length > 1
      ? ((forecastData[forecastData.length - 1]?.base_case || 0) - (forecastData[0]?.base_case || 0)) / forecastData.length
      : 0

    const trendDirection = trend > 0 ? 'Upward' : trend < 0 ? 'Downward' : 'Stable'
    const trendPercent = avgBase > 0 ? ((trend / avgBase) * 100).toFixed(1) : 0

    // Count forecasts entered
    const forecastsEntered = forecastData.length
    const actualsRecorded = forecastData.filter(f => f.actual !== null && f.actual !== undefined).length

    return {
      avgBase: Math.round(avgBase),
      avgOptimistic: Math.round(avgOptimistic),
      avgPessimistic: Math.round(avgPessimistic),
      trend,
      trendDirection,
      trendPercent,
      forecastsEntered,
      actualsRecorded
    }
  }

  const insights = calculateInsights()

  const handleCreateForecast = async (forecastData) => {
    try {
      await apiClient.createDemandForecast(
        forecastData.product_id,
        forecastData.week_number,
        forecastData
      )
      refetch() // Refresh the data
      alert('Forecast created successfully!')
    } catch (error) {
      console.error('Error creating forecast:', error)
      alert('Failed to create forecast')
    }
  }

  // NOTE: Import from AI is now AUTOMATIC!
  // When you run the pipeline, forecasts are automatically synced to database.
  // This function is kept for manual refresh if needed.
  const handleImportFromAI = async () => {
    alert('ℹ️ Forecasts are now automatically synced when you run the AI Pipeline!\n\nGo to Pipeline page → Run Analysis → Forecasts update automatically.\n\nThis manual import is only needed if you want to force refresh.')
    setIsImporting(false)
  }

  const handleOpenForecastModal = async () => {
    // Try to fetch AI data to pre-fill the form
    try {
      const response = await apiClient.getLatestAIForecast(selectedProduct)
      setAIForecastData(response.data)
    } catch (error) {
      // No AI data available, that's okay
      setAIForecastData(null)
    }
    setShowForecastModal(true)
  }

  const runDemandAnalysis = useMutation({
    mutationFn: () =>
      apiClient.runAgent(
        'demand',
        `Provide complete demand intelligence analysis for ${selectedProduct} including forecast accuracy, trend analysis, scenario modeling, and demand-supply alignment recommendations`,
        selectedProduct
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

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Demand Intelligence</h1>
          <p className="mt-1 text-sm text-gray-500">
            AI-powered demand forecasting and scenario analysis
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white text-sm font-medium"
          >
            {products.length > 0 ? (
              products.map(product => (
                <option key={product.id} value={product.id}>
                  {product.id} - {product.name}
                </option>
              ))
            ) : (
              <>
                <option value="PROD-A">PROD-A - Automotive Sensor Unit</option>
                <option value="PROD-B">PROD-B - Industrial Motor Assembly</option>
                <option value="PROD-C">PROD-C - Smart Thermostat</option>
              </>
            )}
          </select>
          <button
            onClick={handleImportFromAI}
            disabled={isImporting}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg flex items-center gap-2 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            title="Import 12 weeks of forecasts from latest AI analysis"
          >
            {isImporting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <TrendingUp className="h-4 w-4" />
            )}
            {isImporting ? 'Importing...' : 'Import from AI'}
          </button>
          <button
            onClick={handleOpenForecastModal}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg flex items-center gap-2 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            Add Forecast
          </button>
        </div>
      </div>

      {/* AI Analysis Tool */}
      <Card>
        <CardHeader>
          <CardTitle>Run Demand Analysis</CardTitle>
          <CardDescription>
            Get AI-powered demand forecasting insights and scenario recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <button
            onClick={() => runDemandAnalysis.mutate()}
            disabled={runDemandAnalysis.isPending}
            className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
          >
            {runDemandAnalysis.isPending ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Analyzing Demand...
              </>
            ) : (
              <>
                <Play className="h-5 w-5" />
                Analyze Demand
              </>
            )}
          </button>
        </CardContent>
      </Card>

      {/* AI Results */}
      {result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <RecommendationCard
            result={result}
            agentType="demand"
            onDismiss={() => setResult(null)}
          />
        </motion.div>
      )}

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Average Weekly Demand"
          value={insights ? `${insights.avgBase.toLocaleString()} units` : '—'}
          subtitle="Base case forecast average"
          trend={insights && insights.trend !== 0 ? `${insights.trend > 0 ? '+' : ''}${insights.trendPercent}%` : null}
          delay={0.1}
        />
        <MetricCard
          title="Forecasts Entered"
          value={`${forecastData.length} weeks`}
          subtitle={insights && insights.actualsRecorded > 0 ? `${insights.actualsRecorded} with actuals recorded` : 'No actuals yet'}
          delay={0.2}
        />
        <MetricCard
          title="Trend Direction"
          value={insights?.trendDirection || 'No data'}
          subtitle={insights && insights.trend !== 0 ? `${insights.trend > 0 ? '+' : ''}${insights.trendPercent}% per week` : 'Insufficient data'}
          delay={0.3}
          badge={insights?.trend > 0 ? "Growing" : insights?.trend < 0 ? "Declining" : null}
        />
      </div>

      {/* Forecast Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
      >
        <Card>
          <CardHeader>
            <CardTitle>Demand Forecast - {selectedProductInfo.name}</CardTitle>
            <CardDescription>{selectedProductInfo.id} • Multi-scenario projection with confidence intervals</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-primary-600" />
              </div>
            ) : forecastData.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500 mb-2">No forecast data for {selectedProductInfo.name}</p>
                <p className="text-sm text-gray-400 mb-4">{selectedProductInfo.id}</p>
                <button
                  onClick={() => setShowForecastModal(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg flex items-center gap-2 mx-auto"
                >
                  <Plus className="h-4 w-4" />
                  Add First Forecast
                </button>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="forecast_date"
                    stroke="#6b7280"
                    tickFormatter={(date) => {
                      if (!date) return ''
                      const d = new Date(date)
                      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                    }}
                    label={{ value: '2026 Weeks', position: 'insideBottom', offset: -5, style: { fontSize: 12, fill: '#9ca3af' } }}
                  />
                  <YAxis stroke="#6b7280" label={{ value: 'Units', angle: -90, position: 'insideLeft', style: { fontSize: 12, fill: '#9ca3af' } }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                    }}
                    labelFormatter={(date) => {
                      if (!date) return 'Week'
                      const d = new Date(date)
                      return `Week of ${d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
                    }}
                    formatter={(value, name) => {
                      if (!value) return ['-', name]
                      return [value.toLocaleString() + ' units', name]
                    }}
                  />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="pessimistic"
                    stackId="1"
                    stroke="#ef4444"
                    fill="#fee2e2"
                    name="Conservative Scenario (25% prob)"
                  />
                  <Area
                    type="monotone"
                    dataKey="base_case"
                    stackId="2"
                    stroke="#0ea5e9"
                    fill="#dbeafe"
                    name="Base Case Forecast (55% prob)"
                  />
                  <Area
                    type="monotone"
                    dataKey="optimistic"
                    stackId="3"
                    stroke="#10b981"
                    fill="#d1fae5"
                    name="Optimistic Scenario (20% prob)"
                  />
                  <Line
                    type="monotone"
                    dataKey="actual"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    dot={{ r: 6 }}
                    name="Actual"
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>
      </motion.div>

      {/* Real Data Analysis */}
      {insights && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle>Forecast Analysis</CardTitle>
              <CardDescription>Data-driven insights from your forecast entries</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-blue-900 mb-2">
                    📊 Forecast Summary
                  </p>
                  <div className="text-sm text-blue-800 space-y-1">
                    <p><strong>{insights.forecastsEntered}</strong> weeks of forecast data entered</p>
                    <p><strong>{insights.actualsRecorded}</strong> weeks with actual demand recorded</p>
                    <p>Average base case: <strong>{insights.avgBase.toLocaleString()} units/week</strong></p>
                    <p>Range: {insights.avgPessimistic.toLocaleString()} (conservative) to {insights.avgOptimistic.toLocaleString()} (optimistic)</p>
                  </div>
                </div>

                {insights.trend !== 0 && (
                  <div className={`p-4 rounded-lg border ${insights.trend > 0 ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
                    <div className="flex items-start gap-2">
                      <TrendingUp className={`h-5 w-5 mt-0.5 ${insights.trend > 0 ? 'text-green-600' : 'text-yellow-600'}`} />
                      <div>
                        <p className={`text-sm font-medium mb-2 ${insights.trend > 0 ? 'text-green-900' : 'text-yellow-900'}`}>
                          {insights.trendDirection} Trend Detected
                        </p>
                        <p className={`text-sm ${insights.trend > 0 ? 'text-green-800' : 'text-yellow-800'}`}>
                          Demand forecast shows a <strong>{insights.trendDirection.toLowerCase()}</strong> trend
                          ({insights.trend > 0 ? '+' : ''}{insights.trendPercent}% per week).
                          {insights.trend > 0
                            ? ' Consider increasing production capacity or supplier orders to meet growing demand.'
                            : ' Review production schedules and inventory levels to avoid overstock.'}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {insights.actualsRecorded === 0 && (
                  <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-amber-900 mb-2">
                          Action Needed: Track Actual Demand
                        </p>
                        <p className="text-sm text-amber-800">
                          No actual demand data recorded yet. Once weeks pass, update forecasts with actual sales
                          to measure forecast accuracy and improve future predictions.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {insights.actualsRecorded > 0 && (
                  <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                    <p className="text-sm font-medium text-purple-900 mb-2">
                      ✅ Forecast Accuracy Tracking Active
                    </p>
                    <p className="text-sm text-purple-800">
                      {insights.actualsRecorded} weeks have actual demand recorded.
                      Continue tracking to calculate forecast accuracy (MAPE) and improve planning precision.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      <ForecastInputModal
        isOpen={showForecastModal}
        onClose={() => {
          setShowForecastModal(false)
          setAIForecastData(null)
        }}
        onSubmit={handleCreateForecast}
        productId={selectedProduct}
        aiSuggestion={aiForeccastData}
      />
    </div>
  )
}

function MetricCard({ title, value, subtitle, trend, badge, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start justify-between mb-3">
            <TrendingUp className="h-5 w-5 text-primary-600" />
            {badge && <Badge variant="warning">{badge}</Badge>}
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            {trend && (
              <span className="text-sm font-medium text-green-600 flex items-center gap-1">
                {trend}
              </span>
            )}
          </div>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </CardContent>
      </Card>
    </motion.div>
  )
}
