import { useState, useEffect, useRef } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
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
} from 'lucide-react'
import Card, { CardHeader, CardTitle, CardContent, CardDescription } from '../components/Card'
import Badge from '../components/Badge'
import { apiClient } from '../lib/api'
import { formatDate } from '../lib/utils'
import { useNotificationStore } from '../store/notificationStore'

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

// Approximate durations (seconds) for each agent in the pipeline
const agentDurations = [18, 16, 14, 20, 18, 12]

function NodeStatus({ status }) {
  if (status === 'running') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-xs font-medium bg-blue-100 text-blue-700">
        <span className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />
        Running
      </span>
    )
  }
  if (status === 'complete') {
    return <span className="inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium bg-green-100 text-green-700">Done</span>
  }
  if (status === 'error') {
    return <span className="inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium bg-red-100 text-red-700">Error</span>
  }
  return <span className="inline-flex items-center rounded-full px-1.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-500">Pending</span>
}

function AgentPipelineVisualizer({ nodeStatuses, nodeElapsed, agentOutputs, onNodeClick, expandedNode }) {
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
                : 'bg-gray-300'

            const lineClass =
              idx < pipelineNodes.length - 1
                ? nodeStatuses[idx] === 'complete' ? 'bg-green-400' : 'bg-gray-200'
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
                  <span className="text-xs font-medium text-gray-700 text-center leading-tight">{node.label}</span>
                  <NodeStatus status={status} />
                  {status === 'running' && elapsed !== undefined && (
                    <span className="text-xs text-blue-600 font-mono">{elapsed}s</span>
                  )}
                  {status === 'complete' && elapsed !== undefined && (
                    <span className="text-xs text-gray-400 font-mono">{elapsed}s</span>
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
          {expandedNode !== null && agentOutputs && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="mt-4 overflow-hidden"
            >
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-semibold text-gray-800">
                    {pipelineNodes[expandedNode]?.label} Output Summary
                  </p>
                </div>
                <p className="text-xs text-gray-600 whitespace-pre-wrap leading-relaxed">
                  {typeof agentOutputs === 'string'
                    ? agentOutputs.split('\n').slice(0, 4).join('\n')
                    : 'Agent completed successfully.'}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </CardContent>
    </Card>
  )
}

export default function Pipeline() {
  const [currentRunId, setCurrentRunId] = useState(null)
  const [productId, setProductId] = useState('PROD-A')

  // Pipeline visualizer state
  const [nodeStatuses, setNodeStatuses] = useState(Array(6).fill('pending'))
  const [nodeElapsed, setNodeElapsed] = useState({})
  const [expandedNode, setExpandedNode] = useState(null)
  const [pipelineTimer, setPipelineTimer] = useState(0)
  const pipelineTimerRef = useRef(null)
  const nodeTimersRef = useRef([])
  const elapsedTimersRef = useRef([])

  // Fetch pipeline run status
  const { data: runData, refetch } = useQuery({
    queryKey: ['pipeline-run', currentRunId],
    queryFn: () => apiClient.getPipelineRun(currentRunId),
    enabled: !!currentRunId,
    refetchInterval: (data) => {
      return data?.data?.status === 'running' || data?.data?.status === 'pending' ? 2000 : false
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
    if (!run) return

    if (run.status === 'completed') {
      setNodeStatuses(Array(6).fill('complete'))
      stopVisualizerAnimation()
    } else if (run.status === 'failed') {
      const completedCount = run.agents_completed?.length || 0
      setNodeStatuses((prev) => {
        const updated = [...prev]
        for (let i = 0; i < completedCount; i++) updated[i] = 'complete'
        if (completedCount < 6) updated[completedCount] = 'error'
        return updated
      })
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
  }, [run])

  function startVisualizerAnimation() {
    // Clear any previous timers
    stopVisualizerAnimation()

    setNodeStatuses(Array(6).fill('pending'))
    setNodeElapsed({})
    setExpandedNode(null)
    setPipelineTimer(0)

    // Pipeline-level timer
    pipelineTimerRef.current = setInterval(() => {
      setPipelineTimer((t) => t + 1)
    }, 1000)

    // Schedule each node transition
    let cumulative = 0
    agentDurations.forEach((duration, idx) => {
      const startDelay = cumulative * 1000

      // Start node
      const startTimer = setTimeout(() => {
        setNodeStatuses((prev) => {
          const updated = [...prev]
          updated[idx] = 'running'
          return updated
        })

        // Per-node elapsed counter
        let sec = 0
        const elapsedTimer = setInterval(() => {
          sec++
          setNodeElapsed((prev) => ({ ...prev, [idx]: sec }))
        }, 1000)
        elapsedTimersRef.current[idx] = elapsedTimer
      }, startDelay)

      nodeTimersRef.current.push(startTimer)
      cumulative += duration

      // Complete node (will be overridden by real data if available)
      const endTimer = setTimeout(() => {
        clearInterval(elapsedTimersRef.current[idx])
        setNodeStatuses((prev) => {
          const updated = [...prev]
          if (updated[idx] === 'running') updated[idx] = 'complete'
          return updated
        })
      }, cumulative * 1000)

      nodeTimersRef.current.push(endTimer)
    })
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
  const totalDuration = run?.completed_at && run?.created_at
    ? Math.round((new Date(run.completed_at) - new Date(run.created_at)) / 1000)
    : null

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Pipeline Runner</h1>
        <p className="mt-1 text-sm text-gray-500">
          Execute full 5-agent manufacturing intelligence analysis
        </p>
      </div>

      {/* Agent Pipeline Visualizer */}
      <AgentPipelineVisualizer
        nodeStatuses={nodeStatuses}
        nodeElapsed={nodeElapsed}
        agentOutputs={run?.result}
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Product ID
                  </label>
                  <input
                    type="text"
                    value={productId}
                    onChange={(e) => setProductId(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                    placeholder="e.g., PROD-A"
                    disabled={isRunning}
                  />
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
                <span className="text-gray-500">Last Run</span>
                <span className="font-medium text-gray-800 text-right text-xs">
                  {lastCompletedRun
                    ? formatDate(lastCompletedRun.created_at)
                    : run?.completed_at
                    ? formatDate(run.completed_at)
                    : '—'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Duration</span>
                <span className="font-medium text-gray-800">
                  {isRunning
                    ? pipelineDurationStr
                    : totalDuration
                    ? `${Math.floor(totalDuration / 60)}m ${totalDuration % 60}s`
                    : '—'}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Success Rate</span>
                <span className="font-medium text-green-600">100%</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Next Scheduled</span>
                <span className="font-medium text-gray-800">Manual trigger</span>
              </div>
              {isRunning && (
                <div className="pt-2 border-t border-gray-100">
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
            <Card className="border-green-200 bg-green-50">
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-green-600 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-green-900 mb-2">
                      Database Automatically Updated
                    </h3>
                    <p className="text-sm text-green-700 mb-3">
                      AI insights have been synced to the database. All tabs now reflect the latest analysis.
                    </p>
                    {run.sync_status.changes_count > 0 && (
                      <div className="space-y-1">
                        <p className="text-xs font-medium text-green-800">
                          Changes Applied ({run.sync_status.changes_count}):
                        </p>
                        {run.sync_status.changes.map((change, idx) => (
                          <p key={idx} className="text-xs text-green-700 pl-4">
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

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Analysis Results</CardTitle>
                  <CardDescription>
                    Completed at {formatDate(run.completed_at)}
                  </CardDescription>
                </div>
                <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 flex items-center gap-2 transition-colors">
                  <Download className="h-4 w-4" />
                  Export
                </button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap text-sm bg-gray-50 p-6 rounded-lg border border-gray-200 max-h-96 overflow-y-auto">
                  {run.result}
                </pre>
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
          <Card className="border-red-200 bg-red-50">
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                <div>
                  <h3 className="text-sm font-semibold text-red-900 mb-1">
                    Pipeline Failed
                  </h3>
                  <p className="text-sm text-red-700">{run.error}</p>
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
          <Card className="border-orange-200">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-orange-500" />
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
            <p className="text-sm text-gray-500 text-center py-8">
              No recent runs. Start an analysis to see results here.
            </p>
          ) : (
            <div className="space-y-3">
              {recentRuns.data.map((run) => (
                <div
                  key={run.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all cursor-pointer"
                  onClick={() => setCurrentRunId(run.id)}
                >
                  <div className="flex items-center gap-3">
                    {run.status === 'completed' ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : run.status === 'failed' ? (
                      <AlertCircle className="h-5 w-5 text-red-600" />
                    ) : (
                      <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
                    )}
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {run.product_id}
                      </p>
                      <p className="text-xs text-gray-500">
                        <Clock className="inline h-3 w-3 mr-1" />
                        {formatDate(run.created_at)}
                      </p>
                    </div>
                  </div>
                  <Badge
                    variant={
                      run.status === 'completed'
                        ? 'success'
                        : run.status === 'failed'
                        ? 'error'
                        : 'info'
                    }
                  >
                    {run.status}
                  </Badge>
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
          ? 'bg-green-50 border-green-200'
          : isCurrent
          ? 'bg-blue-50 border-blue-200 shadow-sm'
          : 'bg-gray-50 border-gray-200'
      }`}
    >
      <div
        className={`p-2 rounded-lg ${
          isCompleted
            ? 'bg-green-100'
            : isCurrent
            ? 'bg-blue-100'
            : 'bg-gray-100'
        }`}
      >
        <agent.icon
          className={`h-5 w-5 ${
            isCompleted
              ? 'text-green-600'
              : isCurrent
              ? 'text-blue-600'
              : 'text-gray-400'
          }`}
        />
      </div>
      <div className="flex-1">
        <p
          className={`text-sm font-medium ${
            isCompleted || isCurrent ? 'text-gray-900' : 'text-gray-500'
          }`}
        >
          {agent.name}
        </p>
      </div>
      {isCompleted ? (
        <CheckCircle className="h-5 w-5 text-green-600" />
      ) : isCurrent ? (
        <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
      ) : null}
    </motion.div>
  )
}

function ApprovalItem({ item, onDecide }) {
  const [modifyMode, setModifyMode] = useState(false)
  const [note, setNote] = useState('')
  const [decided, setDecided] = useState(false)

  const riskColor = {
    low: 'bg-green-100 text-green-700',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-700',
  }

  const agentTypeLabel = {
    demand_forecast_update: 'Demand',
    inventory_adjustment: 'Inventory',
    production_schedule_change: 'Production',
    machine_maintenance: 'Machine Health',
  }

  if (decided) return null

  return (
    <div className="p-4 border border-orange-200 rounded-lg bg-orange-50/40 space-y-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${riskColor[item.risk_level] || 'bg-gray-100 text-gray-700'}`}>
          {item.risk_level?.toUpperCase()} RISK
        </span>
        <span className="text-xs font-medium bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">
          {agentTypeLabel[item.decision_type] || item.decision_type}
        </span>
      </div>
      <p className="text-sm font-semibold text-gray-900">{item.action}</p>
      <p className="text-sm text-gray-600">{item.description}</p>
      {modifyMode && (
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          rows={2}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 resize-none"
          placeholder="Add modification notes..."
        />
      )}
      <div className="flex gap-2 flex-wrap">
        {!modifyMode ? (
          <>
            <button
              onClick={() => { onDecide(item.id, 'approve'); setDecided(true) }}
              className="px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition-colors"
            >
              ✓ Accept & Execute
            </button>
            <button
              onClick={() => setModifyMode(true)}
              className="px-3 py-1.5 border border-blue-500 text-blue-600 text-sm font-medium rounded-lg hover:bg-blue-50 transition-colors"
            >
              ✎ Modify
            </button>
            <button
              onClick={() => { onDecide(item.id, 'reject'); setDecided(true) }}
              className="px-3 py-1.5 border border-gray-300 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
            >
              ✕ Reject
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => { onDecide(item.id, 'modify', note); setDecided(true) }}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Submit
            </button>
            <button
              onClick={() => setModifyMode(false)}
              className="px-3 py-1.5 border border-gray-300 text-gray-600 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </>
        )}
      </div>
    </div>
  )
}
