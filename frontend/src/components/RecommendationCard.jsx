import { useState } from 'react'
import { ChevronDown, ChevronUp, Sparkles } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
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
  'bg-blue-500/15 text-blue-400 border border-blue-500/25',
  'bg-violet-500/15 text-violet-400 border border-violet-500/25',
  'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25',
]

const mdComponents = {
  h1: ({ children }) => <h1 className="text-base font-bold text-white mt-4 mb-2 first:mt-0 pb-1.5 border-b border-slate-700">{children}</h1>,
  h2: ({ children }) => (
    <h2 className="text-sm font-bold text-white mt-4 mb-1.5 first:mt-0 flex items-center gap-2">
      <span className="inline-block w-1 h-3.5 rounded-full bg-primary-500 shrink-0" />
      {children}
    </h2>
  ),
  h3: ({ children }) => <h3 className="text-xs font-bold text-slate-200 mt-3 mb-1 first:mt-0 uppercase tracking-wide">{children}</h3>,
  p: ({ children }) => <p className="text-sm text-slate-200 leading-relaxed mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
  em: ({ children }) => <em className="italic text-slate-300">{children}</em>,
  ul: ({ children }) => <ul className="space-y-1 mb-2 ml-0.5">{children}</ul>,
  ol: ({ children }) => <ol className="space-y-1 mb-2 ml-0.5 list-none">{children}</ol>,
  li: ({ children }) => (
    <li className="flex items-start gap-2 text-sm text-slate-200 leading-relaxed">
      <span className="mt-2 h-1.5 w-1.5 rounded-full bg-primary-400 shrink-0" />
      <span className="flex-1">{children}</span>
    </li>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-primary-500 pl-3 py-0.5 my-2 bg-primary-500/5 rounded-r-lg text-slate-300 italic text-sm">{children}</blockquote>
  ),
  code: ({ inline, children }) =>
    inline ? (
      <code className="px-1.5 py-0.5 rounded bg-slate-700 text-primary-300 font-mono text-xs font-semibold">{children}</code>
    ) : (
      <pre className="bg-slate-800 border border-slate-700 rounded-lg p-3 overflow-x-auto my-2">
        <code className="text-xs font-mono text-slate-200">{children}</code>
      </pre>
    ),
  hr: () => <hr className="border-slate-700 my-3" />,
  table: ({ children }) => (
    <div className="overflow-x-auto my-2 rounded-lg border border-slate-700">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-slate-800">{children}</thead>,
  th: ({ children }) => <th className="px-3 py-2 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">{children}</th>,
  td: ({ children }) => <td className="px-3 py-2 text-sm text-slate-200 border-t border-slate-700/50">{children}</td>,
}

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
  let colorClass = 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'
  if (confidence < 60) colorClass = 'bg-red-500/15 text-red-400 border border-red-500/25'
  else if (confidence < 85) colorClass = 'bg-amber-500/15 text-amber-400 border border-amber-500/25'

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
  const impact = impactChips[agentType] || '↑ Performance improvement'
  const factors = reasoningFactors[agentType] || []
  const agentLabel = agentLabels[agentType] || agentType

  const firstLine = result?.split('\n').find((l) => l.trim().length > 0) || ''
  const decisionTitle = propTitle || firstLine.replace(/^#+\s*/, '').slice(0, 100) || `${agentLabel} recommendation`

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
    <Card className="border-primary-500/30 bg-primary-500/5">
      <CardContent className="p-6">
        {/* Header row */}
        <div className="flex flex-wrap items-center gap-2 mb-4">
          <div className="p-1.5 bg-primary-500/15 border border-primary-500/25 rounded-lg">
            <Sparkles className="h-4 w-4 text-primary-400" />
          </div>
          <span className="text-sm font-semibold text-white">AI Recommendation</span>
          <Badge variant="info" className="ml-1">{agentLabel}</Badge>
          <ConfidenceBadge confidence={confidence} />
        </div>

        {/* Impact row */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">
            {impact}
          </span>
        </div>

        {/* Full result rendered as markdown */}
        <div className="mb-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Analysis</p>
          <div className={`${expanded ? '' : 'max-h-48 overflow-hidden relative'}`}>
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
              {result}
            </ReactMarkdown>
            {!expanded && (
              <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-slate-900 to-transparent pointer-events-none" />
            )}
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs font-medium text-primary-400 hover:text-primary-300 transition-colors mt-2"
          >
            {expanded ? (
              <><ChevronUp className="h-3.5 w-3.5" /> Show less</>
            ) : (
              <><ChevronDown className="h-3.5 w-3.5" /> Show full analysis</>
            )}
          </button>
        </div>

        {/* Reasoning factors */}
        {factors.length > 0 && (
          <div className="mb-5">
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Reasoning Factors</p>
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
            <label className="block text-xs font-medium text-slate-300 mb-1">Add notes / modifications</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-slate-700 rounded-lg text-sm bg-slate-800 text-white placeholder-slate-500 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:outline-none resize-none"
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
                className="px-4 py-2 bg-emerald-600 text-white text-sm font-medium rounded-lg hover:bg-emerald-500 transition-colors flex items-center gap-1.5"
              >
                <span>✓</span> Accept &amp; Execute
              </button>
              <button
                onClick={() => setModifyMode(true)}
                className="px-4 py-2 border border-blue-500/40 text-blue-400 text-sm font-medium rounded-lg hover:bg-blue-500/10 transition-colors flex items-center gap-1.5"
              >
                <span>✎</span> Modify
              </button>
              <button
                onClick={handleDismiss}
                className="px-4 py-2 border border-slate-700 text-slate-400 text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors flex items-center gap-1.5"
              >
                <span>✕</span> Dismiss
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleSubmitNote}
                className="px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-500 transition-colors"
              >
                Submit
              </button>
              <button
                onClick={() => setModifyMode(false)}
                className="px-4 py-2 border border-slate-700 text-slate-400 text-sm font-medium rounded-lg hover:bg-slate-800 transition-colors"
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
