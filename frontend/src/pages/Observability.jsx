import { useQuery } from '@tanstack/react-query'
import {
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  Loader2,
  RefreshCw,
  Zap,
  Database,
} from 'lucide-react'
import Card, { CardHeader, CardTitle, CardContent } from '../components/Card'
import { apiClient } from '../lib/api'
import { formatDate } from '../lib/utils'

// ─── Colour maps ──────────────────────────────────────────────────────────────

const AGENT_COLORS = {
  demand:       { bg: 'bg-blue-500/15',    text: 'text-blue-400',    bar: '#3b82f6' },
  inventory:    { bg: 'bg-purple-500/15',  text: 'text-purple-400',  bar: '#a855f7' },
  machine:      { bg: 'bg-amber-500/15',   text: 'text-amber-400',   bar: '#f59e0b' },
  production:   { bg: 'bg-emerald-500/15', text: 'text-emerald-400', bar: '#10b981' },
  supplier:     { bg: 'bg-rose-500/15',    text: 'text-rose-400',    bar: '#f43f5e' },
  orchestrator: { bg: 'bg-cyan-500/15',    text: 'text-cyan-400',    bar: '#06b6d4' },
  synthesis:    { bg: 'bg-cyan-500/15',    text: 'text-cyan-400',    bar: '#06b6d4' },
}

const AGENT_DEFAULT = { bg: 'bg-slate-700', text: 'text-slate-300', bar: '#64748b' }

function agentColor(type = '') {
  return AGENT_COLORS[type.toLowerCase()] ?? AGENT_DEFAULT
}

// ─── Status badge ─────────────────────────────────────────────────────────────

function StatusBadge({ status }) {
  if (status === 'completed') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium bg-emerald-500/15 text-emerald-400">
        <CheckCircle className="h-3 w-3" />
        Completed
      </span>
    )
  }
  if (status === 'failed') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium bg-red-500/15 text-red-400">
        <XCircle className="h-3 w-3" />
        Failed
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium bg-yellow-500/15 text-yellow-400">
      <Loader2 className="h-3 w-3 animate-spin" />
      Running
    </span>
  )
}

// ─── Summary cards ────────────────────────────────────────────────────────────

function SummaryCard({ icon: Icon, label, value, accent }) {
  return (
    <Card>
      <CardContent className="p-4 flex items-center gap-3">
        <div className={`p-2 rounded-lg ${accent}/15 border ${accent}/25 shrink-0`}>
          <Icon className={`h-5 w-5 ${accent.replace('bg-', 'text-').replace('/15', '')}`} />
        </div>
        <div>
          <p className="text-2xl font-bold text-white leading-none">{value ?? '—'}</p>
          <p className="text-xs text-slate-400 mt-0.5">{label}</p>
        </div>
      </CardContent>
    </Card>
  )
}

// ─── Agent runs list ──────────────────────────────────────────────────────────

function AgentRunsPanel({ runs }) {
  const recent = (runs ?? []).slice(0, 10)

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-white flex items-center gap-2 text-base">
          <Zap className="h-4 w-4 text-cyan-400" />
          Agent Runs
          <span className="text-xs font-normal text-slate-500">recent 10</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 flex-1 overflow-auto">
        {recent.length === 0 ? (
          <p className="text-center text-slate-500 py-10 text-sm">No agent runs recorded yet.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-xs text-slate-500 uppercase tracking-wide">
                <th className="px-4 py-2 text-left">Agent</th>
                <th className="px-4 py-2 text-left">Status</th>
                <th className="px-4 py-2 text-right">Duration</th>
                <th className="px-4 py-2 text-right">Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {recent.map((run) => {
                const { bg, text } = agentColor(run.agent_type)
                const durationSec = run.duration_ms != null
                  ? (run.duration_ms / 1000).toFixed(1) + 's'
                  : '—'
                return (
                  <tr key={run.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-2.5">
                      <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold uppercase ${bg} ${text}`}>
                        {run.agent_type}
                      </span>
                    </td>
                    <td className="px-4 py-2.5">
                      <StatusBadge status={run.status} />
                    </td>
                    <td className="px-4 py-2.5 text-right text-slate-300 font-mono">
                      {durationSec}
                    </td>
                    <td className="px-4 py-2.5 text-right text-slate-500 text-xs whitespace-nowrap">
                      {formatDate(run.created_at)}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Activity log panel ───────────────────────────────────────────────────────

function ActivityLogPanel({ log }) {
  const recent = (log ?? []).slice(0, 15)

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-3">
        <CardTitle className="text-white flex items-center gap-2 text-base">
          <Activity className="h-4 w-4 text-cyan-400" />
          Activity Log
          <span className="text-xs font-normal text-slate-500">recent 15</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 flex-1 overflow-auto">
        {recent.length === 0 ? (
          <p className="text-center text-slate-500 py-10 text-sm">No activity recorded yet.</p>
        ) : (
          <ul className="divide-y divide-slate-800">
            {recent.map((entry) => (
              <li key={entry.id} className="flex items-start gap-3 px-4 py-3 hover:bg-slate-800/40 transition-colors">
                <div className="mt-0.5 shrink-0 p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
                  <Activity className="h-3 w-3 text-cyan-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-white truncate">{entry.action}</p>
                  <p className="text-xs text-slate-400 truncate">{entry.details}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-slate-500">{entry.user}</span>
                    <span className="text-slate-700">·</span>
                    <span className="text-xs text-slate-500">{formatDate(entry.timestamp)}</span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Pipeline trace bar ───────────────────────────────────────────────────────

function PipelineTraceCard({ run }) {
  const totalMs = run.agent_trace?.reduce((sum, s) => sum + (s.duration_ms ?? 0), 0) || run.duration_ms || 1
  const displayDuration = run.duration_ms != null
    ? (run.duration_ms / 1000).toFixed(1) + 's'
    : '—'

  return (
    <Card>
      <CardContent className="p-5">
        {/* Header row */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20">
              <Database className="h-4 w-4 text-cyan-400" />
            </div>
            <div>
              <p className="text-sm font-semibold text-white">{run.product_id ?? 'Pipeline'}</p>
              <p className="text-xs text-slate-500">{formatDate(run.created_at)}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1 text-xs text-slate-400">
              <Clock className="h-3.5 w-3.5" />
              {displayDuration}
            </span>
            <StatusBadge status={run.status} />
          </div>
        </div>

        {/* Trace bar */}
        {!run.agent_trace || run.agent_trace.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No trace data available.</p>
        ) : (
          <>
            {/* Stacked horizontal bar */}
            <div className="flex w-full h-8 rounded-lg overflow-hidden gap-px">
              {run.agent_trace.map((seg, idx) => {
                const pct = ((seg.duration_ms ?? 0) / totalMs) * 100
                const { bar } = agentColor(seg.agent)
                return (
                  <div
                    key={idx}
                    title={`${seg.label ?? seg.agent}: ${(seg.duration_ms / 1000).toFixed(1)}s, ${seg.tools_called ?? 0} tools`}
                    style={{ width: `${pct}%`, backgroundColor: bar, minWidth: '4px' }}
                    className="h-full transition-all duration-300"
                  />
                )
              })}
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-3 mt-3">
              {run.agent_trace.map((seg, idx) => {
                const { bar, text } = agentColor(seg.agent)
                const secStr = seg.duration_ms != null
                  ? (seg.duration_ms / 1000).toFixed(1) + 's'
                  : '—'
                return (
                  <div key={idx} className="flex items-center gap-1.5">
                    <span
                      className="h-2.5 w-2.5 rounded-sm shrink-0"
                      style={{ backgroundColor: bar }}
                    />
                    <span className={`text-xs font-medium ${text}`}>
                      {seg.label ?? seg.agent}
                    </span>
                    <span className="text-xs text-slate-500">{secStr}</span>
                    {seg.tools_called != null && (
                      <span className="text-xs text-slate-600">· {seg.tools_called} tools</span>
                    )}
                  </div>
                )
              })}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function Observability() {
  const { data, isLoading, isError, refetch, isFetching } = useQuery({
    queryKey: ['observability'],
    queryFn: async () => {
      const res = await apiClient.getObservability()
      return res.data
    },
    refetchInterval: 10000,
    staleTime: 0,
  })

  const summary = data?.summary ?? {}
  const agentRuns = data?.agent_runs ?? []
  const pipelineRuns = data?.pipeline_runs ?? []
  const activityLog = data?.activity_log ?? []

  return (
    <div className="space-y-6">
      {/* ── Header ── */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">Observability</h1>
          <p className="mt-1 text-sm text-slate-400">
            Live agent activity, run history and system traces
          </p>
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white text-sm font-medium transition-colors disabled:opacity-50 shrink-0"
        >
          <RefreshCw className={`h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* ── Summary cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
        <SummaryCard icon={Activity}     label="Total Runs"      value={summary.total_agent_runs}    accent="bg-cyan-500" />
        <SummaryCard icon={Database}     label="Pipeline Runs"   value={summary.total_pipeline_runs} accent="bg-purple-500" />
        <SummaryCard icon={Loader2}      label="Active"          value={summary.active_runs}         accent="bg-yellow-500" />
        <SummaryCard icon={CheckCircle}  label="Completed"       value={summary.completed_runs}      accent="bg-emerald-500" />
        <SummaryCard icon={XCircle}      label="Failed"          value={summary.failed_runs}         accent="bg-red-500" />
      </div>

      {/* ── Loading / error states ── */}
      {isLoading && (
        <div className="flex items-center justify-center py-16 gap-3 text-slate-400">
          <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
          <span className="text-sm">Loading observability data…</span>
        </div>
      )}

      {isError && !isLoading && (
        <Card>
          <CardContent className="py-12 text-center">
            <XCircle className="h-8 w-8 text-red-400 mx-auto mb-3" />
            <p className="text-sm text-slate-400">Failed to load observability data.</p>
            <button
              onClick={() => refetch()}
              className="mt-4 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-sm font-medium transition-colors"
            >
              Retry
            </button>
          </CardContent>
        </Card>
      )}

      {/* ── Two-column: agent runs + activity log ── */}
      {!isLoading && !isError && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <AgentRunsPanel runs={agentRuns} />
            <ActivityLogPanel log={activityLog} />
          </div>

          {/* ── Pipeline traces ── */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold text-white">Pipeline Traces</h2>
              <span className="text-xs text-slate-500 font-normal">
                ({pipelineRuns.length} run{pipelineRuns.length !== 1 ? 's' : ''})
              </span>
              {isFetching && (
                <Loader2 className="h-3.5 w-3.5 text-cyan-400 animate-spin ml-1" />
              )}
            </div>

            {pipelineRuns.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <Database className="h-8 w-8 text-slate-600 mx-auto mb-3" />
                  <p className="text-sm text-slate-500">No pipeline runs recorded yet.</p>
                </CardContent>
              </Card>
            ) : (
              pipelineRuns.map((run) => (
                <PipelineTraceCard key={run.id} run={run} />
              ))
            )}
          </div>
        </>
      )}
    </div>
  )
}
