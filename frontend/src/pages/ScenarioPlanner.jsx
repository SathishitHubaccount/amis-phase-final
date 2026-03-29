import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, GitBranch, CheckCircle, TrendingUp, TrendingDown, Minus } from 'lucide-react'
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

const baseState = {
  demandPerWeek: 1050,
  inventoryDays: 18.7,
  oee: 87.3,
  productionGap: -5,
  riskLevel: 'Low',
}

function parseScenario(text) {
  const lower = text.toLowerCase()

  if ((lower.includes('supplier') || lower.includes('sup')) && lower.includes('delay')) {
    return {
      demandPerWeek: 1050,
      inventoryDays: 12.4,
      oee: 87.3,
      productionGap: -105,
      riskLevel: 'High',
      recommendation: 'Expedite PO with SUP-001 for 3,500 units at premium freight (+$4,200). Activate safety stock drawdown protocol. Alert production scheduling for potential 2-week capacity reduction.',
      highlights: [
        'Lead time +7 days increases stockout risk by 25%',
        'Safety stock will be breached within 6 days at current burn rate',
        'Recommend activating secondary supplier SUP-003 immediately',
      ],
    }
  }

  if ((lower.includes('demand') || lower.includes('spike')) && (lower.includes('30') || lower.includes('%'))) {
    return {
      demandPerWeek: 1365,
      inventoryDays: 10.2,
      oee: 87.3,
      productionGap: -315,
      riskLevel: 'Critical',
      recommendation: 'Authorize 20h overtime on Lines 1-3 for weeks 13-16. Increase supplier PO by 2,100 units/week. Adjust safety stock target to 700 units. Expected fulfillment impact: 3-4 week delay without action.',
      highlights: [
        'Demand spike of +315 units/week exceeds current capacity',
        'Overtime authorization required within 48 hours',
        'Supplier lead time may become bottleneck — dual-source activation advised',
      ],
    }
  }

  if (lower.includes('mch-002') || (lower.includes('machine') && lower.includes('down'))) {
    return {
      demandPerWeek: 1050,
      inventoryDays: 16.8,
      oee: 78.8,
      productionGap: -57,
      riskLevel: 'High',
      recommendation: 'Reschedule 57 units/week to Line 3 and Line 4. Expedite MCH-002 bearing replacement (ETA 3 days). Implement predictive monitoring on MCH-003 as precaution. Estimated revenue risk: $28,500/week.',
      highlights: [
        'OEE drops 8.5% with MCH-002 offline',
        'Production gap of 52 units/week requires rescheduling',
        'Line 3 has 18% spare capacity available for absorption',
      ],
    }
  }

  if (lower.includes('shortage') || lower.includes('material')) {
    return {
      demandPerWeek: 1050,
      inventoryDays: 14.7,
      oee: 87.3,
      productionGap: -80,
      riskLevel: 'High',
      recommendation: 'Activate dual-source procurement for affected components. Negotiate emergency allocation with SUP-001 (Priority Class A). Consider partial production run prioritizing highest-margin SKUs. Estimated cost increase: +12% on affected components.',
      highlights: [
        'Inventory days reduced by 4 due to component shortage',
        'Component cost increases 12% under shortage conditions',
        'Dual-source activation can restore 60% of affected supply within 5 days',
      ],
    }
  }

  return {
    demandPerWeek: 1050,
    inventoryDays: 17.2,
    oee: 85.9,
    productionGap: -20,
    riskLevel: 'Medium',
    recommendation: 'Monitor situation closely. Current buffers provide 3-5 day response window. Review safety stock levels and ensure supplier contingency plans are activated if conditions worsen.',
    highlights: [
      'Moderate impact detected based on scenario analysis',
      'Current buffers provide adequate response time',
      'Recommend increasing monitoring frequency',
    ],
  }
}

function DeltaValue({ current, base, suffix = '', lowerIsBetter = false }) {
  const delta = current - base
  const isPositive = delta > 0
  const isBetter = lowerIsBetter ? !isPositive : isPositive
  const isNeutral = Math.abs(delta) < 0.1

  if (isNeutral) {
    return (
      <span className="inline-flex items-center gap-1 text-gray-500">
        <Minus className="h-3.5 w-3.5" />
        <span>{current.toFixed(1)}{suffix}</span>
      </span>
    )
  }

  return (
    <span className={`inline-flex items-center gap-1 ${isBetter ? 'text-green-600' : 'text-red-600'}`}>
      {isBetter ? (
        <TrendingUp className="h-3.5 w-3.5" />
      ) : (
        <TrendingDown className="h-3.5 w-3.5" />
      )}
      <span>{current.toFixed(1)}{suffix}</span>
      <span className="text-xs">({delta > 0 ? '+' : ''}{delta.toFixed(1)}{suffix})</span>
    </span>
  )
}

export default function ScenarioPlanner() {
  const [scenarioText, setScenarioText] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState(null)
  const [showSuccess, setShowSuccess] = useState(false)
  const [history, setHistory] = useState([])

  const addNotification = useNotificationStore((state) => state.addNotification)

  const handleAnalyze = async () => {
    if (!scenarioText.trim()) return
    setIsAnalyzing(true)
    setResults(null)

    await new Promise((resolve) => setTimeout(resolve, 2000))

    const impact = parseScenario(scenarioText)
    setResults(impact)
    setIsAnalyzing(false)
    setHistory((prev) => [
      { text: scenarioText, timestamp: new Date().toISOString(), riskLevel: impact.riskLevel },
      ...prev.slice(0, 2),
    ])
  }

  const handleAcceptRecommendation = async () => {
    addNotification({
      title: 'Scenario Recommendation Accepted',
      message: `Scenario "${scenarioText.slice(0, 60)}" — recommendation queued for execution`,
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

  const riskBadgeVariant = {
    Low: 'success',
    Medium: 'warning',
    High: 'error',
    Critical: 'error',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">What-If Scenario Planner</h1>
        <p className="mt-1 text-sm text-gray-500">
          Model disruptions and optimize decisions before they happen
        </p>
      </div>

      {/* Success Toast */}
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
              Recommendation accepted and added to the notification queue.
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Scenario Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-primary-600" />
            Describe Your Scenario
          </CardTitle>
          <CardDescription>
            Describe a disruption, constraint, or what-if situation to model its impact
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

          {/* Quick Scenario Buttons */}
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

          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing || !scenarioText.trim()}
            className="px-6 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Analyzing Scenario...
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

      {/* Results */}
      <AnimatePresence>
        {results && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-4"
          >
            {/* Side-by-side comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Current State */}
              <Card className="border-gray-200">
                <CardHeader>
                  <CardTitle className="text-base text-gray-700">Current State</CardTitle>
                  <CardDescription>Baseline metrics before scenario</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Demand/week</span>
                      <span className="font-semibold text-gray-900">{baseState.demandPerWeek.toLocaleString()} units</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Inventory Days</span>
                      <span className="font-semibold text-gray-900">{baseState.inventoryDays} days</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">OEE</span>
                      <span className="font-semibold text-gray-900">{baseState.oee}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Production Gap</span>
                      <span className="font-semibold text-gray-900">{baseState.productionGap} units/wk</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Risk Level</span>
                      <Badge variant={riskBadgeVariant[baseState.riskLevel]}>{baseState.riskLevel}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Projected Impact */}
              <Card className="border-red-200 bg-red-50/30">
                <CardHeader>
                  <CardTitle className="text-base text-red-700">Projected Impact</CardTitle>
                  <CardDescription>After applying scenario</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Demand/week</span>
                      <DeltaValue current={results.demandPerWeek} base={baseState.demandPerWeek} suffix=" units" />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Inventory Days</span>
                      <DeltaValue current={results.inventoryDays} base={baseState.inventoryDays} suffix=" days" lowerIsBetter />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">OEE</span>
                      <DeltaValue current={results.oee} base={baseState.oee} suffix="%" />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Production Gap</span>
                      <DeltaValue current={results.productionGap} base={baseState.productionGap} suffix=" units/wk" />
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Risk Level</span>
                      <Badge variant={riskBadgeVariant[results.riskLevel]}>{results.riskLevel}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* AI Recommendation */}
            <Card className="border-primary-200">
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-base">
                  <span>AI Recommendation</span>
                  <Badge variant="success">89% confidence</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {results.highlights && (
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

      {/* Scenario History */}
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
                    <p className="text-xs text-gray-500 mt-0.5">
                      {new Date(item.timestamp).toLocaleString()}
                    </p>
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
