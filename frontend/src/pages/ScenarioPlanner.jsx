import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, GitBranch, CheckCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import { useNotificationStore } from '../store/notificationStore'
import { apiClient } from '../lib/api'

const quickScenarios = [
  'Supplier delay 2 weeks',
  'Demand spike +30%',
  'MCH-002 goes down',
  'Raw material shortage',
]

function DeltaValue({ current, base, suffix = '', lowerIsBetter = false }) {
  const delta = current - base
  const isPositive = delta > 0
  const isBetter = lowerIsBetter ? !isPositive : isPositive
  const isNeutral = Math.abs(delta) < 0.1

  if (isNeutral) {
    return (
      <span className="inline-flex items-center gap-1 text-gray-500">
        <Minus className="h-3.5 w-3.5" />
        <span>{typeof current === 'number' ? current.toFixed(1) : current}{suffix}</span>
      </span>
    )
  }

  return (
    <span className={`inline-flex items-center gap-1 ${isBetter ? 'text-green-600' : 'text-red-600'}`}>
      {isBetter ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
      <span>{typeof current === 'number' ? current.toFixed(1) : current}{suffix}</span>
      <span className="text-xs">({delta > 0 ? '+' : ''}{typeof delta === 'number' ? delta.toFixed(1) : delta}{suffix})</span>
    </span>
  )
}

export default function ScenarioPlanner() {
  const [scenarioText, setScenarioText] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState(null)
  const [baseState, setBaseState] = useState(null)
  const [showSuccess, setShowSuccess] = useState(false)
  const [history, setHistory] = useState([])
  const [error, setError] = useState(null)

  const addNotification = useNotificationStore((state) => state.addNotification)

  // Load real base state from dashboard
  const { data: dashData } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => apiClient.getDashboardSummary(),
  })

  const handleAnalyze = async () => {
    if (!scenarioText.trim()) return
    setIsAnalyzing(true)
    setResults(null)
    setError(null)

    try {
      const res = await apiClient.analyzeScenario(scenarioText)
      const data = res.data
      setBaseState(data.base_state)
      setResults({
        projected: data.projected,
        recommendation: data.recommendation,
        highlights: data.highlights,
        confidence: data.confidence,
      })
      setHistory((prev) => [
        { text: scenarioText, timestamp: new Date().toISOString(), riskLevel: data.projected?.riskLevel || 'Medium' },
        ...prev.slice(0, 2),
      ])
    } catch (err) {
      setError(err?.response?.data?.detail || 'Analysis failed. Make sure the backend is running.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleAcceptRecommendation = async () => {
    addNotification({
      title: 'Scenario Recommendation Accepted',
      message: `"${scenarioText.slice(0, 60)}" — recommendation queued for execution`,
      category: 'pipeline',
      severity: 'info',
    })
    const user = JSON.parse(localStorage.getItem('user') || '{"username":"Manager"}')
    const actionBy = user.full_name || user.username || 'Manager'
    try {
      await apiClient.saveDecision(
        'scenario',
        scenarioText.slice(0, 120),
        'Accepted',
        actionBy,
        null,
        results?.recommendation || ''
      )
    } catch (e) {
      console.error('Failed to save scenario decision:', e)
    }
    setShowSuccess(true)
    setTimeout(() => setShowSuccess(false), 4000)
  }

  const riskBadgeVariant = { Low: 'success', Medium: 'warning', High: 'error', Critical: 'error' }

  // Derive base state: prefer real API data, fall back to dashboard summary
  const displayBase = baseState || {
    demandPerWeek: parseInt((dashData?.data?.metrics?.demand?.value || '1050').replace(/,/g, '')) || 1050,
    inventoryDays: parseFloat(dashData?.data?.metrics?.inventory?.value) || 14.0,
    oee: parseFloat(dashData?.data?.metrics?.machines?.oee) || 85.0,
    productionGap: dashData?.data?.metrics?.production?.gap || 0,
    riskLevel: 'Low',
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">What-If Scenario Planner</h1>
        <p className="mt-1 text-sm text-gray-500">
          Model disruptions and optimize decisions before they happen — powered by real factory data
        </p>
      </div>

      <AnimatePresence>
        {showSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex items-center gap-3 p-4 bg-green-50 border border-green-200 rounded-xl"
          >
            <CheckCircle className="h-5 w-5 text-green-600 shrink-0" />
            <p className="text-sm font-medium text-green-800">
              Recommendation accepted and saved to audit log.
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-primary-600" />
            Describe Your Scenario
          </CardTitle>
          <CardDescription>
            Claude AI will analyze the impact using your real factory data
          </CardDescription>
        </CardHeader>
        <CardContent>
          <textarea
            value={scenarioText}
            onChange={(e) => setScenarioText(e.target.value)}
            rows={4}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none mb-4"
            placeholder={`Examples:\n• "What if Supplier A delays by 2 weeks?"\n• "What if demand spikes +30% in weeks 13-16?"\n• "What if MCH-002 goes offline for maintenance?"`}
          />
          <div className="flex flex-wrap gap-2 mb-4">
            {quickScenarios.map((scenario) => (
              <button
                key={scenario}
                onClick={() => setScenarioText(scenario)}
                className="px-3 py-1.5 text-xs font-medium text-primary-700 bg-primary-50 border border-primary-200 rounded-full hover:bg-primary-100 transition-colors"
              >
                {scenario}
              </button>
            ))}
          </div>
          {error && (
            <p className="text-sm text-red-600 mb-3 p-3 bg-red-50 rounded-lg border border-red-200">{error}</p>
          )}
          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !scenarioText.trim()}
            className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Analyzing with Claude AI...
              </>
            ) : (
              <>
                <GitBranch className="h-5 w-5" />
                Analyze Scenario
              </>
            )}
          </button>
        </CardContent>
      </Card>

      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Current State */}
              <Card className="border-gray-200">
                <CardHeader>
                  <CardTitle className="text-base text-gray-700">Current State</CardTitle>
                  <CardDescription>Real baseline from your factory database</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Demand/week</span>
                      <span className="font-semibold text-gray-900">{displayBase.demandPerWeek.toLocaleString()} units</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Inventory Days</span>
                      <span className="font-semibold text-gray-900">{displayBase.inventoryDays} days</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">OEE</span>
                      <span className="font-semibold text-gray-900">{displayBase.oee}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Production Gap</span>
                      <span className="font-semibold text-gray-900">{displayBase.productionGap} units/wk</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Risk Level</span>
                      <Badge variant={riskBadgeVariant[displayBase.riskLevel] || 'success'}>{displayBase.riskLevel}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Projected Impact */}
              <Card className="border-red-200 bg-red-50/30">
                <CardHeader>
                  <CardTitle className="text-base text-red-700">Projected Impact</CardTitle>
                  <CardDescription>AI analysis after applying scenario</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Demand/week</span>
                      <DeltaValue current={results.projected.demandPerWeek} base={displayBase.demandPerWeek} suffix=" units" />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Inventory Days</span>
                      <DeltaValue current={results.projected.inventoryDays} base={displayBase.inventoryDays} suffix=" days" lowerIsBetter />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">OEE</span>
                      <DeltaValue current={results.projected.oee} base={displayBase.oee} suffix="%" />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Production Gap</span>
                      <DeltaValue current={results.projected.productionGap} base={displayBase.productionGap} suffix=" units/wk" />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Risk Level</span>
                      <Badge variant={riskBadgeVariant[results.projected.riskLevel] || 'warning'}>{results.projected.riskLevel}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Before / After Visual Comparison Chart */}
            <Card className="border-gray-200">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary-600" />
                  Impact Comparison
                </CardTitle>
                <CardDescription>Side-by-side view of current vs projected metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={[
                        {
                          metric: 'Demand (÷10)',
                          Current: Math.round(displayBase.demandPerWeek / 10),
                          Projected: Math.round((results.projected.demandPerWeek || displayBase.demandPerWeek) / 10),
                        },
                        {
                          metric: 'Inventory Days',
                          Current: displayBase.inventoryDays,
                          Projected: results.projected.inventoryDays || displayBase.inventoryDays,
                        },
                        {
                          metric: 'OEE %',
                          Current: displayBase.oee,
                          Projected: results.projected.oee || displayBase.oee,
                        },
                        {
                          metric: 'Prod Gap (÷10)',
                          Current: Math.round(Math.abs(displayBase.productionGap || 0) / 10),
                          Projected: Math.round(Math.abs(results.projected.productionGap || 0) / 10),
                        },
                      ]}
                      margin={{ top: 10, right: 20, left: 0, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                      <XAxis dataKey="metric" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                      <Legend wrapperStyle={{ fontSize: 12 }} />
                      <Bar dataKey="Current" fill="#3b82f6" radius={[4, 4, 0, 0]} maxBarSize={40} />
                      <Bar dataKey="Projected" fill="#f59e0b" radius={[4, 4, 0, 0]} maxBarSize={40} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* AI Recommendation */}
            <Card className="border-primary-200">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-base">
                  <span>AI Recommendation</span>
                  <Badge variant="success">{Math.round((results.confidence || 0.85) * 100)}% confidence</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {results.highlights && results.highlights.length > 0 && (
                  <ul className="space-y-1 mb-4">
                    {results.highlights.map((h, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                        <span className="text-primary-500 mt-0.5 shrink-0">•</span>
                        {h}
                      </li>
                    ))}
                  </ul>
                )}
                <p className="text-sm text-gray-700 mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  {results.recommendation}
                </p>
                <button
                  onClick={handleAcceptRecommendation}
                  className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  Accept Recommendation
                </button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Scenarios</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {history.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-start justify-between p-3 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{item.text}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{new Date(item.timestamp).toLocaleString()}</p>
                  </div>
                  <Badge variant={riskBadgeVariant[item.riskLevel] || 'default'} className="ml-3 shrink-0">
                    {item.riskLevel}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
