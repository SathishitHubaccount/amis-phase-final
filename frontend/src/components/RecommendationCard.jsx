import { useState } from 'react'
import { ChevronDown, ChevronUp, Sparkles } from 'lucide-react'
import Card, { CardContent } from './Card'
import Badge from './Badge'
import { useNotificationStore } from '../store/notificationStore'
import { apiClient } from '../lib/api'

const agentLabels = {
  demand: 'Demand Intelligence',
  inventory: 'Inventory Control',
  machine: 'Machine Health',
  production: 'Production Planning',
  supplier: 'Supplier Management',
}

const impactChips = {
  machine: '↓ 30-50% downtime risk',
  inventory: '↓ 15-25% stockout risk',
  demand: '↑ 20% forecast accuracy',
  production: '↑ 8-15% throughput',
  supplier: '↓ 40% delivery risk',
}

const reasoningFactors = {
  machine: ['Vibration Pattern', 'Temperature Trend', 'Runtime Hours'],
  inventory: ['Demand Variability', 'Lead Time Risk', 'Safety Stock Gap'],
  demand: ['Historical Trend', 'Seasonal Pattern', 'Market Context'],
  production: ['Capacity Gap', 'Bottleneck Analysis', 'OEE Impact'],
  supplier: ['OTD Performance', 'Risk Score', 'Contract Terms'],
}

const factorColors = [
  'bg-blue-100 text-blue-700',
  'bg-purple-100 text-purple-700',
  'bg-green-100 text-green-700',
]

function extractConfidence(result) {
  if (!result) return 87
  const match = result.match(/(\d+)%/)
  if (match) {
    const val = parseInt(match[1], 10)
    if (val >= 1 && val <= 100) return val
  }
  return 87
}

function ConfidenceBadge({ confidence }) {
  let colorClass = 'bg-green-100 text-green-700'
  if (confidence < 60) colorClass = 'bg-red-100 text-red-700'
  else if (confidence < 85) colorClass = 'bg-yellow-100 text-yellow-700'

  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${colorClass}`}>
      {confidence}% confidence
    </span>
  )
}

export default function RecommendationCard({ result, agentType, title: propTitle, onDismiss }) {
  const [expanded, setExpanded] = useState(false)
  const [modifyMode, setModifyMode] = useState(false)
  const [note, setNote] = useState('')
  const addNotification = useNotificationStore((state) => state.addNotification)

  const confidence = extractConfidence(result)
  const lines = result
    ? result.split('\n').filter((l) => l.trim().length > 0)
    : []
  const keyFindings = lines.slice(0, 5)
  const impact = impactChips[agentType] || '↑ Performance improvement'
  const factors = reasoningFactors[agentType] || []
  const agentLabel = agentLabels[agentType] || agentType

  // Derive a short title from the first line of the result or the prop
  const decisionTitle = propTitle || lines[0]?.slice(0, 100) || `${agentLabel} recommendation`

  // Read logged-in user for action_by
  const user = JSON.parse(localStorage.getItem('user') || '{"username":"Manager"}')
  const actionBy = user.full_name || user.username || 'Manager'

  const handleAccept = async () => {
    addNotification({
      title: 'Recommendation Accepted',
      message: 'Recommendation accepted and queued for execution',
      category: agentType,
      severity: 'info',
    })
    try {
      await apiClient.saveDecision(agentType, decisionTitle, 'Accepted', actionBy, null, result)
    } catch (e) {
      console.error('Failed to save decision:', e)
    }
    onDismiss()
  }

  const handleSubmitNote = async () => {
    addNotification({
      title: 'Recommendation Modified',
      message: `Recommendation modified: ${note || '(no notes)'}`,
      category: agentType,
      severity: 'info',
    })
    try {
      await apiClient.saveDecision(agentType, decisionTitle, 'Modified', actionBy, note, result)
    } catch (e) {
      console.error('Failed to save decision:', e)
    }
    onDismiss()
  }

  const handleDismiss = async () => {
    try {
      await apiClient.saveDecision(agentType, decisionTitle, 'Dismissed', actionBy, null, result)
    } catch (e) {
      console.error('Failed to save decision:', e)
    }
    onDismiss()
  }

  return (
    <Card className="border-primary-200">
      <CardContent className="p-6">
        {/* Header row */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <div className="p-1.5 bg-primary-50 rounded-lg">
            <Sparkles className="h-4 w-4 text-primary-600" />
          </div>
          <span className="text-sm font-semibold text-gray-900">AI Recommendation</span>
          <Badge variant="info" className="ml-1">{agentLabel}</Badge>
          <ConfidenceBadge confidence={confidence} />
        </div>

        {/* Impact row */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium bg-green-100 text-green-700">
            {impact}
          </span>
        </div>

        {/* Key Findings */}
        {keyFindings.length > 0 && (
          <div className="mb-4">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Key Findings</p>
            <ul className="space-y-1">
              {keyFindings.map((line, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-primary-500 mt-0.5 shrink-0">•</span>
                  <span>{line}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Full Analysis collapsible */}
        <div className="mb-4">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs font-medium text-primary-600 hover:text-primary-800 transition-colors"
          >
            {expanded ? (
              <>
                <ChevronUp className="h-3.5 w-3.5" />
                Hide Full Analysis
              </>
            ) : (
              <>
                <ChevronDown className="h-3.5 w-3.5" />
                Show Full Analysis
              </>
            )}
          </button>
          {expanded && (
            <div className="mt-3">
              <pre className="whitespace-pre-wrap text-xs bg-gray-50 p-4 rounded-lg border border-gray-200 max-h-64 overflow-y-auto text-gray-700 leading-relaxed">
                {result}
              </pre>
            </div>
          )}
        </div>

        {/* Reasoning factors */}
        {factors.length > 0 && (
          <div className="mb-5">
            <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Reasoning Factors</p>
            <div className="flex flex-wrap gap-2">
              {factors.map((factor, idx) => (
                <span
                  key={factor}
                  className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${factorColors[idx % factorColors.length]}`}
                >
                  {factor}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Modify inline textarea */}
        {modifyMode && (
          <div className="mb-4">
            <label className="block text-xs font-medium text-gray-700 mb-1">Add notes / modifications</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
              placeholder="Describe your modifications..."
            />
          </div>
        )}

        {/* Action buttons */}
        <div className="flex flex-wrap gap-2">
          {!modifyMode ? (
            <>
              <button
                onClick={handleAccept}
                className="px-4 py-2 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors flex items-center gap-1.5"
              >
                <span>✓</span> Accept &amp; Execute
              </button>
              <button
                onClick={() => setModifyMode(true)}
                className="px-4 py-2 border border-blue-500 text-blue-600 text-sm font-medium rounded-lg hover:bg-blue-50 transition-colors flex items-center gap-1.5"
              >
                <span>✎</span> Modify
              </button>
              <button
                onClick={handleDismiss}
                className="px-4 py-2 border border-gray-300 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-1.5"
              >
                <span>✕</span> Dismiss
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleSubmitNote}
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Submit
              </button>
              <button
                onClick={() => setModifyMode(false)}
                className="px-4 py-2 border border-gray-300 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
