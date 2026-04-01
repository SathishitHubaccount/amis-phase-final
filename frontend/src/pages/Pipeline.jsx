import { useState, useEffect, useRef } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Play,
  CheckCircle,
  Loader2,
  AlertCircle,
  TrendingUp,
  Package,
  Cog,
  Factory,
  Truck,
  Target,
  Clock,
  Download,
  Layers,
  ChevronDown,
  ChevronUp,
  Eye,
  EyeOff,
  ArrowRight,
  Wrench,
  Zap,
} from 'lucide-react'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import { apiClient } from '../lib/api'
import { formatDate } from '../lib/utils'
import { useNotificationStore } from '../store/notificationStore'

const markdownComponents = {
  h1: ({ children }) => <h1 className="text-xl font-black text-white mt-5 mb-3 first:mt-0 pb-2 border-b border-slate-700">{children}</h1>,
  h2: ({ children }) => (
    <h2 className="text-base font-bold text-white mt-5 mb-2.5 first:mt-0 flex items-center gap-2">
      <span className="inline-block w-1 h-4 rounded-full bg-primary-500 shrink-0" />
      {children}
    </h2>
  ),
  h3: ({ children }) => <h3 className="text-sm font-bold text-slate-200 mt-4 mb-2 first:mt-0">{children}</h3>,
  p: ({ children }) => <p className="text-sm text-slate-200 leading-relaxed mb-3 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
  em: ({ children }) => <em className="italic text-slate-300">{children}</em>,
  ul: ({ children }) => <ul className="space-y-1.5 mb-3 ml-1">{children}</ul>,
  ol: ({ children }) => <ol className="space-y-1.5 mb-3 ml-1 list-none">{children}</ol>,
  li: ({ children }) => (
    <li className="flex items-start gap-2.5 text-sm text-slate-200 leading-relaxed">
      <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary-400 shrink-0" />
      <span className="flex-1">{children}</span>
    </li>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-primary-500 pl-4 py-1 my-3 bg-primary-500/5 rounded-r-lg text-slate-300 italic text-sm">{children}</blockquote>
  ),
  code: ({ inline, children }) =>
    inline ? (
      <code className="px-1.5 py-0.5 rounded bg-slate-700 text-primary-300 font-mono text-xs font-semibold">{children}</code>
    ) : (
      <pre className="bg-slate-800 border border-slate-700 rounded-xl p-4 overflow-x-auto my-3">
        <code className="text-xs font-mono text-slate-200">{children}</code>
      </pre>
    ),
  hr: () => <hr className="border-slate-700 my-4" />,
  table: ({ children }) => (
    <div className="overflow-x-auto my-3 rounded-xl border border-slate-700">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-slate-800">{children}</thead>,
  th: ({ children }) => <th className="px-4 py-2.5 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">{children}</th>,
  td: ({ children }) => <td className="px-4 py-2.5 text-sm text-slate-200 border-t border-slate-700/50">{children}</td>,
}

const agents = [
  { id: 'demand', name: 'Demand Forecasting', icon: TrendingUp, color: 'text-blue-600' },
  { id: 'inventory', name: 'Inventory Management', icon: Package, color: 'text-green-600' },
  { id: 'machine', name: 'Machine Health', icon: Cog, color: 'text-yellow-600' },
  { id: 'production', name: 'Production Planning', icon: Factory, color: 'text-purple-600' },
  { id: 'supplier', name: 'Supplier & Procurement', icon: Truck, color: 'text-orange-600' },
]

const pipelineNodes = [
  { id: 'demand', label: 'Demand', icon: TrendingUp },
  { id: 'inventory', label: 'Inventory', icon: Package },
  { id: 'machine', label: 'Machine', icon: Cog },
  { id: 'production', label: 'Production', icon: Factory },
  { id: 'supplier', label: 'Supplier', icon: Truck },
  { id: 'synthesis', label: 'Synthesis', icon: Layers },
]


function NodeStatus({ status }) {
  if (status === 'running') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-xs font-medium bg-blue-500/15 text-blue-400 border border-blue-500/25">
        <span className="h-1.5 w-1.5 rounded-full bg-blue-400 animate-pulse" />
        Running
      </span>
    )
  }
  if (status === 'complete') {
    return <span className="inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/25">Done</span>
  }
  if (status === 'error') {
    return <span className="inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium bg-red-500/15 text-red-400 border border-red-500/25">Error</span>
  }
  return <span className="inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium bg-slate-700 text-slate-500">Pending</span>
}

function AgentPipelineVisualizer({ nodeStatuses, nodeElapsed, agentTrace, onNodeClick, expandedNode }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Pipeline Flow
        </CardTitle>
        <CardDescription>Agent execution sequence — click a completed node to view output</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-start gap-0 overflow-x-auto pb-2">
          {pipelineNodes.map((node, idx) => {
            const NodeIcon = node.icon
            const status = nodeStatuses[idx] || 'pending'
            const elapsed = nodeElapsed[idx]

            const nodeCircleClass =
              status === 'running'
                ? 'bg-blue-500 animate-pulse shadow-lg shadow-blue-500/40'
                : status === 'complete'
                ? 'bg-green-500'
                : status === 'error'
                ? 'bg-red-500'
                : 'bg-slate-700'

            const lineClass =
              idx < pipelineNodes.length - 1
                ? nodeStatuses[idx] === 'complete' ? 'bg-green-400' : 'bg-slate-700'
                : ''

            return (
              <div key={node.id} className="flex items-center">
                {/* Node */}
                <button
                  onClick={() => status === 'complete' && onNodeClick(idx)}
                  className={`flex flex-col items-center gap-1.5 min-w-[72px] group ${status === 'complete' ? 'cursor-pointer' : 'cursor-default'}`}
                  title={status === 'complete' ? 'Click to view output' : node.label}
                >
                  <div
                    className={`h-12 w-12 rounded-full flex items-center justify-center transition-all ${nodeCircleClass} ${status === 'complete' ? 'group-hover:scale-110' : ''}`}
                  >
                    <NodeIcon className="h-5 w-5 text-white" />
                  </div>
                  <span className="text-xs font-medium text-slate-300 text-center leading-tight">{node.label}</span>
                  <NodeStatus status={status} />
                  {status === 'running' && elapsed !== undefined && (
                    <span className="text-xs text-blue-600 font-mono">{elapsed}s</span>
                  )}
                  {status === 'complete' && elapsed !== undefined && (
                    <span className="text-xs text-slate-500 font-mono">{elapsed}s</span>
                  )}
                </button>

                {/* Connecting line */}
                {idx < pipelineNodes.length - 1 && (
                  <div className={`h-0.5 w-8 shrink-0 transition-colors duration-500 ${lineClass}`} />
                )}
              </div>
            )
          })}
        </div>

        {/* Expanded node output */}
        <AnimatePresence>
          {expandedNode !== null && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="mt-4 overflow-hidden"
            >
              {(() => {
                const traceStep = agentTrace?.[expandedNode]
                const node = pipelineNodes[expandedNode]
                return (
                  <div className="p-4 bg-slate-900 rounded-lg border border-slate-800">
                    <p className="text-sm font-semibold text-slate-200 mb-3">
                      {node?.label} — Quick Summary
                    </p>
                    {traceStep ? (
                      <div className="space-y-2">
                        <div className="grid grid-cols-2 gap-2">
                          {traceStep.key_findings?.map((f) => (
                            <div key={f.label} className="bg-slate-900 rounded border border-slate-800 px-2.5 py-1.5">
                              <p className="text-[10px] text-slate-500">{f.label}</p>
                              <p className="text-xs font-semibold text-slate-200">{f.value}</p>
                            </div>
                          ))}
                        </div>
                        <p className="text-[10px] text-slate-500 pt-1">
                          {traceStep.tools_called?.length} tools called · {((traceStep.duration_ms || 0) / 1000).toFixed(2)}s
                        </p>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500">Agent completed successfully.</p>
                    )}
                  </div>
                )
              })()}
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}

// ─── colour maps ─────────────────────────────────────────────────────────────
const AGENT_STYLES = {
  demand:     { bg: 'bg-blue-500/8',    border: 'border-blue-500/25',    dot: 'bg-blue-500',    text: 'text-blue-400',    badge: 'bg-blue-500/15 text-blue-400 border border-blue-500/25',    num: 'bg-blue-500' },
  inventory:  { bg: 'bg-violet-500/8',  border: 'border-violet-500/25',  dot: 'bg-violet-500',  text: 'text-violet-400',  badge: 'bg-violet-500/15 text-violet-400 border border-violet-500/25',  num: 'bg-violet-500' },
  machine:    { bg: 'bg-amber-500/8',   border: 'border-amber-500/25',   dot: 'bg-amber-500',   text: 'text-amber-400',   badge: 'bg-amber-500/15 text-amber-400 border border-amber-500/25',   num: 'bg-amber-500' },
  production: { bg: 'bg-emerald-500/8', border: 'border-emerald-500/25', dot: 'bg-emerald-500', text: 'text-emerald-400', badge: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25', num: 'bg-emerald-500' },
  supplier:   { bg: 'bg-rose-500/8',    border: 'border-rose-500/25',    dot: 'bg-rose-500',    text: 'text-rose-400',    badge: 'bg-rose-500/15 text-rose-400 border border-rose-500/25',    num: 'bg-rose-500' },
}

function PipelineTracePanel({ structuredResult }) {
  const [open, setOpen] = useState(true)
  const [expandedAgent, setExpandedAgent] = useState(null)

  const trace = structuredResult?.pipeline_trace
  if (!trace || trace.length === 0) return null

  const totalTools = trace.reduce((s, t) => s + t.tools_called.length, 0)
  const totalMs = trace.reduce((s, t) => s + (t.duration_ms || 0), 0)
  const totalSec = (totalMs / 1000).toFixed(1)

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="rounded-2xl border border-slate-700 bg-slate-900 overflow-hidden shadow-xl">

        {/* ── Header ──────────────────────────────────────────── */}
        <button
          onClick={() => setOpen((v) => !v)}
          className="w-full flex items-center justify-between px-8 py-5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 border-b border-slate-700 hover:from-indigo-500/15 hover:to-violet-500/15 transition-all"
        >
          <div className="flex items-center gap-4">
            <div className="p-2.5 rounded-xl bg-indigo-500/15 border border-indigo-500/25">
              {open ? <EyeOff className="h-5 w-5 text-indigo-400" /> : <Eye className="h-5 w-5 text-indigo-400" />}
            </div>
            <div className="text-left">
              <p className="text-base font-bold text-white tracking-tight">
                Behind the Scenes — How the AI Decided
              </p>
              <p className="text-sm text-slate-400 mt-0.5">
                Each agent ran independently, then passed insights to the next
              </p>
            </div>
          </div>
          <div className="flex items-center gap-6">
            {/* Summary stats */}
            <div className="hidden md:flex items-center gap-6 pr-4 border-r border-slate-700">
              <div className="text-center">
                <p className="text-2xl font-black text-white">{trace.length}</p>
                <p className="text-xs text-slate-500 font-medium">Agents</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-black text-indigo-400">{totalTools}</p>
                <p className="text-xs text-slate-500 font-medium">Tool Calls</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-black text-emerald-400">{totalSec}s</p>
                <p className="text-xs text-slate-500 font-medium">Total Time</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-sm font-semibold text-indigo-400">
                <Zap className="h-3.5 w-3.5" />
                Live AI Reasoning
              </span>
              {open ? <ChevronUp className="h-5 w-5 text-slate-500 ml-1" /> : <ChevronDown className="h-5 w-5 text-slate-500 ml-1" />}
            </div>
          </div>
        </button>

        {/* ── Body ────────────────────────────────────────────── */}
        <AnimatePresence initial={false}>
          {open && (
            <motion.div
              key="trace-body"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.35, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              {/* Flow connector row */}
              <div className="flex items-start gap-0 px-8 pt-6 pb-4 overflow-x-auto">
                {trace.map((step, idx) => {
                  const s = AGENT_STYLES[step.agent] || AGENT_STYLES.demand
                  const isActive = expandedAgent === idx
                  return (
                    <div key={step.agent} className="flex items-center shrink-0">
                      <button
                        onClick={() => setExpandedAgent(isActive ? null : idx)}
                        className={`flex flex-col items-center gap-2 px-4 py-3 rounded-xl border-2 transition-all min-w-[110px] ${
                          isActive
                            ? `${s.border} ${s.bg} shadow-lg`
                            : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                        }`}
                      >
                        <div className={`w-10 h-10 rounded-full ${s.num} flex items-center justify-center shadow-lg`}>
                          <span className="text-white text-sm font-black">{idx + 1}</span>
                        </div>
                        <span className={`text-xs font-bold text-center leading-tight ${isActive ? s.text : 'text-slate-300'}`}>
                          {step.label.replace(' Agent', '')}
                        </span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${s.badge}`}>
                          {step.tools_called.length} tools
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">
                          {((step.duration_ms || 0) / 1000).toFixed(1)}s
                        </span>
                      </button>
                      {idx < trace.length - 1 && (
                        <div className="flex items-center px-1">
                          <div className="h-0.5 w-8 bg-gradient-to-r from-slate-600 to-slate-600" />
                          <ArrowRight className="h-4 w-4 text-slate-600 -ml-1" />
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>

              {/* Expanded agent detail */}
              <AnimatePresence>
                {expandedAgent !== null && trace[expandedAgent] && (() => {
                  const step = trace[expandedAgent]
                  const s = AGENT_STYLES[step.agent] || AGENT_STYLES.demand
                  return (
                    <motion.div
                      key={expandedAgent}
                      initial={{ opacity: 0, y: -8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -8 }}
                      transition={{ duration: 0.25 }}
                      className={`mx-6 mb-6 rounded-2xl border-2 ${s.border} overflow-hidden shadow-2xl`}
                    >
                      {/* Agent header stripe */}
                      <div className={`px-7 py-5 ${s.bg} flex items-center justify-between`}>
                        <div className="flex items-center gap-4">
                          <div className={`w-12 h-12 rounded-2xl ${s.num} flex items-center justify-center shadow-lg`}>
                            <span className="text-white text-xl font-black">{expandedAgent + 1}</span>
                          </div>
                          <div>
                            <p className={`text-2xl font-black ${s.text}`}>{step.label}</p>
                            <p className="text-sm text-slate-300 mt-0.5 font-medium">
                              {step.tools_called.length} tools executed &nbsp;·&nbsp; {((step.duration_ms || 0) / 1000).toFixed(1)}s runtime
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 bg-emerald-500/15 border border-emerald-500/30 px-4 py-2 rounded-xl">
                          <CheckCircle className="h-5 w-5 text-emerald-400" />
                          <span className="text-sm font-bold text-emerald-400">Completed</span>
                        </div>
                      </div>

                      <div className="bg-slate-900 p-7 space-y-7">

                        {/* KEY FINDINGS — large bright stat cards */}
                        {step.key_findings?.length > 0 && (
                          <div>
                            <p className={`text-sm font-black uppercase tracking-widest mb-4 flex items-center gap-2 ${s.text}`}>
                              <span className={`inline-block w-1 h-4 rounded-full ${s.num}`} />
                              Key Findings
                            </p>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                              {step.key_findings.map((f) => {
                                const isAlert = f.value.includes('⚠') || f.value.toLowerCase().startsWith('yes')
                                return (
                                  <div key={f.label} className={`rounded-2xl border-2 p-5 ${isAlert ? 'border-red-500/40 bg-red-500/10' : `${s.border} ${s.bg}`}`}>
                                    <p className={`text-xs font-bold uppercase tracking-wider mb-2 ${isAlert ? 'text-red-400' : 'text-slate-300'}`}>{f.label}</p>
                                    <p className={`text-3xl font-black leading-none ${isAlert ? 'text-red-300' : s.text}`}>
                                      {f.value}
                                    </p>
                                  </div>
                                )
                              })}
                            </div>
                          </div>
                        )}

                        {/* CLAUDE'S ANALYSIS */}
                        {step.llm_reasoning && (
                          <div className={`rounded-2xl border-2 ${s.border} p-6`} style={{ background: 'rgba(15,23,42,0.8)' }}>
                            <p className={`text-sm font-black uppercase tracking-widest mb-4 flex items-center gap-2 ${s.text}`}>
                              <Zap className="h-5 w-5" />
                              Claude's Analysis
                            </p>
                            <div className="text-base text-slate-100 leading-relaxed font-medium prose prose-invert max-w-none">
                              <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                                {step.llm_reasoning}
                              </ReactMarkdown>
                            </div>
                          </div>
                        )}

                        {/* TOOLS CALLED — clear numbered rows */}
                        <div>
                          <p className={`text-sm font-black uppercase tracking-widest mb-4 flex items-center gap-2 ${s.text}`}>
                            <Wrench className="h-5 w-5" />
                            Tools Executed in Order
                          </p>
                          <div className="space-y-2">
                            {step.tools_called.map((tool) => (
                              <div key={tool.order} className={`flex items-center gap-4 px-5 py-4 rounded-xl border ${s.border} bg-slate-800/80`}>
                                {/* Step number */}
                                <div className={`w-8 h-8 rounded-lg ${s.num} flex items-center justify-center shrink-0`}>
                                  <span className="text-white text-sm font-black">{tool.order}</span>
                                </div>
                                {/* Tool name */}
                                <code className={`text-sm font-bold font-mono ${s.text} shrink-0 min-w-[180px]`}>
                                  {tool.name}
                                </code>
                                {/* Divider */}
                                <div className="w-px h-6 bg-slate-700 shrink-0" />
                                {/* Description */}
                                <p className="text-sm text-slate-200 font-medium flex-1">
                                  {tool.desc || '—'}
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* PASSED TO NEXT */}
                        {step.passed_to_next && (
                          <div className={`flex items-center gap-4 p-5 rounded-2xl border-2 ${s.border} ${s.bg}`}>
                            <div className={`p-2.5 rounded-xl ${s.num}`}>
                              <ArrowRight className="h-5 w-5 text-white" />
                            </div>
                            <div className="flex-1">
                              <p className="text-sm font-bold text-white mb-2">
                                Passed to <span className={`${s.text}`}>{step.passed_to_next.agent}</span>
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {step.passed_to_next.fields.map((field) => (
                                  <span key={field} className={`text-sm font-mono font-semibold ${s.text} bg-slate-800 px-3 py-1 rounded-lg border ${s.border}`}>
                                    {field}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )
                })()}
              </AnimatePresence>

              {/* Bottom hint if nothing expanded */}
              {expandedAgent === null && (
                <p className="text-center text-sm text-slate-600 pb-6">
                  ↑ Click any agent above to see its full reasoning and findings
                </p>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default function Pipeline() {
  const queryClient = useQueryClient()
  const [currentRunId, setCurrentRunId] = useState(null)
  const [productId, setProductId] = useState('PROD-A')

  const { data: productsData } = useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await apiClient.getProducts()
      return response.data.products || response.data || []
    }
  })
  const products = productsData || []

  // Pipeline visualizer state
  const [nodeStatuses, setNodeStatuses] = useState(Array(6).fill('pending'))
  const [nodeElapsed, setNodeElapsed] = useState({})
  const [expandedNode, setExpandedNode] = useState(null)
  const [pipelineTimer, setPipelineTimer] = useState(0)
  const pipelineTimerRef = useRef(null)
  const nodeTimersRef = useRef([])
  const elapsedTimersRef = useRef([])

  // Fetch pipeline run status
  const { data: runData, refetch, isError: runIsError } = useQuery({
    queryKey: ['pipeline-run', currentRunId],
    queryFn: () => apiClient.getPipelineRun(currentRunId),
    enabled: !!currentRunId,
    retry: false,
    // React Query v5: refetchInterval receives the Query object, not data
    refetchInterval: (query) => {
      const s = query.state.data?.data?.status
      return s === 'running' || s === 'pending' ? 500 : false
    },
  })

  // Fetch recent runs
  const { data: recentRuns } = useQuery({
    queryKey: ['pipeline-runs'],
    queryFn: () => apiClient.listPipelineRuns(5),
  })

  // Pending approvals query
  const { data: approvalsData, refetch: refetchApprovals } = useQuery({
    queryKey: ['pending-approvals'],
    queryFn: async () => {
      const res = await apiClient.getPendingApprovals()
      return res.data.pending
    },
    refetchInterval: 10000,
  })
  const pendingApprovals = approvalsData || []

  const addNotification = useNotificationStore((state) => state.addNotification)

  const handleApprovalDecision = async (decisionId, action, notes = null) => {
    const user = JSON.parse(localStorage.getItem('user') || '{"username":"Manager"}')
    await apiClient.decideApproval(decisionId, action, user.full_name || user.username || 'Manager', notes)
    refetchApprovals()
    addNotification({
      title: action === 'approve' ? 'Decision Approved & Executed' : action === 'reject' ? 'Decision Rejected' : 'Decision Modified',
      message: `AI recommendation has been ${action}d and database updated.`,
      severity: action === 'approve' ? 'info' : 'medium',
      category: 'pipeline',
    })
  }

  // Start pipeline mutation
  const startPipeline = useMutation({
    mutationFn: (productId) => apiClient.runPipeline(productId),
    onSuccess: (data) => {
      setCurrentRunId(data.data.run_id)
      refetch()
      startVisualizerAnimation()
    },
  })

  const run = runData?.data
  const status = run?.status
  const isRunning = status === 'running' || status === 'pending'

  // Sync visualizer with real run data
  useEffect(() => {
    // Run not found (server restarted) — stop timer and reset
    if (runIsError) {
      stopVisualizerAnimation()
      setCurrentRunId(null)
      return
    }

    if (!run) return

    if (run.status === 'completed') {
      setNodeStatuses(Array(6).fill('complete'))
      stopVisualizerAnimation()
      queryClient.invalidateQueries({ queryKey: ['pipeline-runs'] })
    } else if (run.status === 'failed') {
      const completedCount = run.agents_completed?.length || 0
      setNodeStatuses((prev) => {
        const updated = [...prev]
        for (let i = 0; i < completedCount; i++) updated[i] = 'complete'
        if (completedCount < 6) updated[completedCount] = 'error'
        return updated
      })
      queryClient.invalidateQueries({ queryKey: ['pipeline-runs'] })
      stopVisualizerAnimation()
    } else if (run.status === 'running' && run.agents_completed) {
      const completedCount = run.agents_completed.length
      setNodeStatuses((prev) => {
        const updated = [...prev]
        for (let i = 0; i < completedCount; i++) updated[i] = 'complete'
        if (completedCount < 6) updated[completedCount] = 'running'
        return updated
      })
    }
  }, [run, runIsError])

  function startVisualizerAnimation() {
    // Clear any previous timers
    stopVisualizerAnimation()

    // Reset all node state — polling (useEffect on `run`) drives completions
    setNodeStatuses((prev) => {
      const updated = Array(6).fill('pending')
      updated[0] = 'running' // node 0 is always running immediately
      return updated
    })
    setNodeElapsed({})
    setExpandedNode(null)
    setPipelineTimer(0)

    // Pipeline-level timer — counts up until stopVisualizerAnimation is called
    pipelineTimerRef.current = setInterval(() => {
      setPipelineTimer((t) => t + 1)
    }, 1000)
  }

  function stopVisualizerAnimation() {
    if (pipelineTimerRef.current) clearInterval(pipelineTimerRef.current)
    nodeTimersRef.current.forEach(clearTimeout)
    elapsedTimersRef.current.forEach(clearInterval)
    nodeTimersRef.current = []
    elapsedTimersRef.current = []
  }

  const handleNodeClick = (idx) => {
    setExpandedNode(expandedNode === idx ? null : idx)
  }

  const pipelineDurationStr = (() => {
    const m = Math.floor(pipelineTimer / 60)
    const s = pipelineTimer % 60
    return `${m}m ${s}s`
  })()

  // Last run stats
  const lastCompletedRun = recentRuns?.data?.find((r) => r.status === 'completed')
  const totalDuration = run?.completed_at && run?.started_at
    ? Math.round((new Date(run.completed_at) - new Date(run.started_at)) / 1000)
    : null
  const successRate = recentRuns?.data?.length
    ? Math.round((recentRuns.data.filter((r) => r.status === 'completed').length / recentRuns.data.length) * 100)
    : null

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Pipeline Runner</h1>
        <p className="mt-1 text-sm text-slate-400">
          Execute full 5-agent manufacturing intelligence analysis
        </p>
      </div>

      {/* Agent Pipeline Visualizer */}
      <AgentPipelineVisualizer
        nodeStatuses={nodeStatuses}
        nodeElapsed={nodeElapsed}
        agentTrace={run?.structured_result?.pipeline_trace}
        onNodeClick={handleNodeClick}
        expandedNode={expandedNode}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Run Controls */}
        <div className="lg:col-span-2">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-end gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Product
                  </label>
                  <select
                    value={productId}
                    onChange={(e) => setProductId(e.target.value)}
                    disabled={isRunning}
                    className="w-full px-4 py-2.5 border border-slate-700 bg-slate-800 text-white rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors text-sm"
                  >
                    {products.length > 0 ? (
                      products.map(p => (
                        <option key={p.id} value={p.id}>{p.name} ({p.id})</option>
                      ))
                    ) : (
                      <>
                        <option value="PROD-A">Industrial Valve Assembly - Type A (PROD-A)</option>
                        <option value="PROD-B">Industrial Valve Assembly - Type B (PROD-B)</option>
                        <option value="PROD-C">Industrial Valve Assembly - Type C (PROD-C)</option>
                      </>
                    )}
                  </select>
                </div>
                <button
                  onClick={() => startPipeline.mutate(productId)}
                  disabled={isRunning || !productId}
                  className="px-8 py-2.5 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
                >
                  {isRunning ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      Running... {pipelineDurationStr}
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5" />
                      Run Analysis
                    </>
                  )}
                </button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Pipeline Health Sidebar */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Pipeline Health</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Last Run</span>
                <span className="font-medium text-slate-200 text-right text-xs">
                  {lastCompletedRun
                    ? formatDate(lastCompletedRun.created_at)
                    : run?.completed_at
                    ? formatDate(run.completed_at)
                    : '—'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Duration</span>
                <span className="font-medium text-slate-200">
                  {isRunning
                    ? pipelineDurationStr
                    : totalDuration
                    ? `${Math.floor(totalDuration / 60)}m ${totalDuration % 60}s`
                    : '—'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Success Rate</span>
                <span className={`font-medium ${successRate === 100 ? 'text-green-600' : successRate !== null && successRate < 80 ? 'text-red-600' : 'text-yellow-600'}`}>
                  {successRate !== null ? `${successRate}%` : '—'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">Next Scheduled</span>
                <span className="font-medium text-slate-200">Manual trigger</span>
              </div>
              {isRunning && (
                <div className="pt-2 border-t border-slate-800">
                  <div className="flex items-center gap-2 text-xs text-blue-600">
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    Pipeline running — {pipelineDurationStr}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Agent Progress */}
      {currentRunId && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Agent Execution</span>
                <Badge
                  variant={
                    status === 'completed'
                      ? 'success'
                      : status === 'failed'
                      ? 'error'
                      : 'info'
                  }
                >
                  {status}
                </Badge>
              </CardTitle>
              <CardDescription>Run ID: {currentRunId}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {agents.map((agent, index) => {
                  const isCompleted = run?.agents_completed?.includes(agent.id)
                  const isCurrent =
                    isRunning &&
                    run?.agents_completed?.length === index &&
                    !isCompleted
                  const isPending = !isCompleted && !isCurrent

                  return (
                    <AgentProgressItem
                      key={agent.id}
                      agent={agent}
                      isCompleted={isCompleted}
                      isCurrent={isCurrent}
                      isPending={isPending}
                      delay={index * 0.1}
                    />
                  )
                })}

                {/* Orchestrator */}
                <AgentProgressItem
                  agent={{
                    id: 'orchestrator',
                    name: 'Cross-Domain Synthesis',
                    icon: Target,
                    color: 'text-pink-600',
                  }}
                  isCompleted={status === 'completed'}
                  isCurrent={
                    isRunning && run?.agents_completed?.length === agents.length
                  }
                  isPending={
                    status === 'pending' ||
                    (isRunning && run?.agents_completed?.length < agents.length)
                  }
                  delay={0.6}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Results */}
      {run?.status === 'completed' && run?.result && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-4"
        >
          {/* Database Sync Status */}
          {run?.sync_status && (
            <Card className="border-emerald-500/30 bg-emerald-500/8">
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-emerald-300 mb-2">
                      Database Automatically Updated
                    </h3>
                    <p className="text-sm text-emerald-400/80 mb-3">
                      AI insights have been synced to the database. All tabs now reflect the latest analysis.
                    </p>
                    {run.sync_status.changes_count > 0 && (
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-emerald-400">
                          Changes Applied ({run.sync_status.changes_count}):
                        </p>
                        {run.sync_status.changes.map((change, idx) => (
                          <p key={idx} className="text-xs text-emerald-400/70 pl-4">
                            • {change}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Behind the Scenes — Agent Trace */}
          <PipelineTracePanel structuredResult={run?.structured_result} />

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Analysis Results</CardTitle>
                  <CardDescription>
                    Completed at {formatDate(run.completed_at)}
                  </CardDescription>
                </div>
                <button className="px-4 py-2 border border-slate-700 text-slate-300 rounded-lg hover:bg-slate-800 flex items-center gap-2 transition-colors">
                  <Download className="h-4 w-4" />
                  Export
                </button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="bg-slate-900 p-6 rounded-lg border border-slate-800 max-h-[32rem] overflow-y-auto">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                  {run.result}
                </ReactMarkdown>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Error Display */}
      {run?.status === 'failed' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="border-red-500/30 bg-red-500/8">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-400 mt-0.5" />
                <div>
                  <h3 className="text-sm font-semibold text-red-300 mb-1">
                    Pipeline Failed
                  </h3>
                  <p className="text-sm text-red-400/80">{run.error}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Pending Approvals */}
      {pendingApprovals.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="border-amber-500/30 bg-amber-500/5">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-amber-400" />
                  Pending Manager Approvals
                </span>
                <Badge variant="warning">{pendingApprovals.length} awaiting decision</Badge>
              </CardTitle>
              <CardDescription>
                These AI recommendations require your approval before they update the database
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {pendingApprovals.map((item) => (
                <ApprovalItem
                  key={item.id}
                  item={item}
                  onDecide={handleApprovalDecision}
                />
              ))}
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Recent Runs */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Pipeline Runs</CardTitle>
        </CardHeader>
        <CardContent>
          {!recentRuns?.data || recentRuns.data.length === 0 ? (
            <p className="text-sm text-slate-400 text-center py-8">
              No recent runs. Start an analysis to see results here.
            </p>
          ) : (
            <div className="space-y-3">
              {recentRuns.data.map((pastRun) => (
                <div
                  key={pastRun.id}
                  className={`flex items-center justify-between p-4 rounded-lg border transition-all cursor-pointer ${
                    pastRun.id === currentRunId
                      ? 'border-primary-500/40 bg-primary-500/8 shadow-sm shadow-primary-500/10'
                      : 'border-slate-800 hover:border-slate-700 hover:shadow-sm'
                  }`}
                  onClick={() => setCurrentRunId(pastRun.id)}
                >
                  <div className="flex items-center gap-3">
                    {pastRun.status === 'completed' ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : pastRun.status === 'failed' ? (
                      <AlertCircle className="h-5 w-5 text-red-600" />
                    ) : (
                      <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-white">
                        {products.find(p => p.id === pastRun.product_id)?.name || pastRun.product_id}
                      </p>
                      <p className="text-xs text-slate-400">
                        <Clock className="inline h-3 w-3 mr-1" />
                        {formatDate(pastRun.completed_at || pastRun.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {pastRun.completed_at && pastRun.started_at && (
                      <span className="text-xs text-slate-500 font-mono">
                        {Math.round((new Date(pastRun.completed_at) - new Date(pastRun.started_at)) / 1000)}s
                      </span>
                    )}
                    <Badge
                      variant={
                        pastRun.status === 'completed'
                          ? 'success'
                          : pastRun.status === 'failed'
                          ? 'error'
                          : 'info'
                      }
                    >
                      {pastRun.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function AgentProgressItem({ agent, isCompleted, isCurrent, isPending, delay }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay }}
      className={`flex items-center gap-4 p-4 rounded-lg border transition-all ${
        isCompleted
          ? 'bg-emerald-500/8 border-emerald-500/25'
          : isCurrent
          ? 'bg-blue-500/8 border-blue-500/25 shadow-lg shadow-blue-500/10'
          : 'bg-slate-900 border-slate-800'
      }`}
    >
      <div
        className={`p-2 rounded-lg ${
          isCompleted
            ? 'bg-emerald-500/15'
            : isCurrent
            ? 'bg-blue-500/15'
            : 'bg-slate-800'
        }`}
      >
        <agent.icon
          className={`h-5 w-5 ${
            isCompleted
              ? 'text-emerald-400'
              : isCurrent
              ? 'text-blue-400'
              : 'text-slate-500'
          }`}
        />
      </div>
      <div className="flex-1">
        <p
          className={`text-sm font-medium ${
            isCompleted || isCurrent ? 'text-white' : 'text-slate-500'
          }`}
        >
          {agent.name}
        </p>
      </div>
      {isCompleted ? (
        <CheckCircle className="h-5 w-5 text-emerald-400" />
      ) : isCurrent ? (
        <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
      ) : null}
    </motion.div>
  )
}

function ApprovalItem({ item, onDecide }) {
  const [modifyMode, setModifyMode] = useState(false)
  const [note, setNote] = useState('')
  const [decided, setDecided] = useState(false)

  const riskConfig = {
    low:      { pill: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30', accent: 'border-l-emerald-500', glow: '' },
    medium:   { pill: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',       accent: 'border-l-amber-500',   glow: '' },
    high:     { pill: 'bg-orange-500/15 text-orange-400 border border-orange-500/30',     accent: 'border-l-orange-500',  glow: 'shadow-orange-500/5' },
    critical: { pill: 'bg-red-500/15 text-red-400 border border-red-500/30',             accent: 'border-l-red-500',     glow: 'shadow-red-500/10' },
  }

  const agentTypeLabel = {
    demand_forecast_update: 'Demand',
    inventory_adjustment: 'Inventory',
    production_schedule_change: 'Production',
    machine_maintenance: 'Machine Health',
  }

  if (decided) return null

  const rc = riskConfig[item.risk_level] || riskConfig.medium

  return (
    <div className={`relative border-l-4 ${rc.accent} bg-slate-800/50 border border-slate-700 rounded-r-xl rounded-bl-xl p-5 space-y-3 shadow-lg ${rc.glow}`}>
      <div className="flex flex-wrap items-center gap-2">
        <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full tracking-wide ${rc.pill}`}>
          {item.risk_level?.toUpperCase()} RISK
        </span>
        <span className="text-xs font-medium bg-slate-700 text-slate-300 border border-slate-600 px-2.5 py-0.5 rounded-full">
          {agentTypeLabel[item.decision_type] || item.decision_type}
        </span>
      </div>
      <p className="text-sm font-semibold text-white leading-snug">{item.action}</p>
      <p className="text-sm text-slate-400 leading-relaxed">{item.description}</p>
      {modifyMode && (
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-slate-600 bg-slate-900 text-white rounded-lg text-sm focus:ring-2 focus:ring-primary-500 resize-none placeholder-slate-500"
          placeholder="Add modification notes..."
        />
      )}
      <div className="flex gap-2 flex-wrap pt-1">
        {!modifyMode ? (
          <>
            <button
              onClick={() => { onDecide(item.id, 'approve'); setDecided(true) }}
              className="px-4 py-1.5 bg-gradient-to-r from-emerald-600 to-emerald-500 text-white text-sm font-semibold rounded-lg hover:from-emerald-500 hover:to-emerald-400 transition-all shadow-lg shadow-emerald-500/20 flex items-center gap-1.5"
            >
              <CheckCircle className="h-3.5 w-3.5" /> Accept & Execute
            </button>
            <button
              onClick={() => setModifyMode(true)}
              className="px-4 py-1.5 border border-blue-500/40 text-blue-400 text-sm font-medium rounded-lg hover:bg-blue-500/10 transition-colors flex items-center gap-1.5"
            >
              ✎ Modify
            </button>
            <button
              onClick={() => { onDecide(item.id, 'reject'); setDecided(true) }}
              className="px-4 py-1.5 border border-slate-600 text-slate-400 text-sm font-medium rounded-lg hover:bg-slate-700 hover:text-slate-300 transition-colors"
            >
              ✕ Reject
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => { onDecide(item.id, 'modify', note); setDecided(true) }}
              className="px-4 py-1.5 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-500 transition-colors"
            >
              Submit Changes
            </button>
            <button
              onClick={() => setModifyMode(false)}
              className="px-4 py-1.5 border border-slate-600 text-slate-400 text-sm font-medium rounded-lg hover:bg-slate-700 transition-colors"
            >
              Cancel
            </button>
          </>
        )}
      </div>
    </div>
  )
}
