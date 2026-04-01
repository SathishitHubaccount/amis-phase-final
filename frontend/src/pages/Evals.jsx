import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, XCircle, Play, Loader2, FlaskConical, AlertTriangle, Zap } from 'lucide-react'
import Card from '../components/Card'

// ─── helpers ────────────────────────────────────────────────────────────────

function formatDuration(ms) {
  if (!ms) return '—'
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

// ─── sub-components ─────────────────────────────────────────────────────────

function PassFailBadge({ passed }) {
  return passed ? (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-semibold text-emerald-400 ring-1 ring-emerald-500/30">
      <CheckCircle className="h-3.5 w-3.5" />
      PASS
    </span>
  ) : (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-500/15 px-3 py-1 text-xs font-semibold text-rose-400 ring-1 ring-rose-500/30">
      <XCircle className="h-3.5 w-3.5" />
      FAIL
    </span>
  )
}

function CheckItem({ check, index }) {
  return (
    <motion.li
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.04, duration: 0.25 }}
      className="flex items-start gap-3 rounded-lg px-3 py-2.5 transition-colors hover:bg-slate-800/60"
    >
      <span className="mt-0.5 shrink-0">
        {check.passed ? (
          <CheckCircle className="h-4 w-4 text-emerald-400" />
        ) : (
          <XCircle className="h-4 w-4 text-rose-400" />
        )}
      </span>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wide">
            {check.category}
          </span>
          {check.required && (
            <span className="rounded px-1.5 py-0.5 text-[10px] font-semibold bg-amber-500/15 text-amber-400 ring-1 ring-amber-500/25">
              required
            </span>
          )}
          <span className="ml-auto text-[11px] font-mono text-slate-500">{check.id}</span>
        </div>
        <p className="mt-0.5 text-sm text-slate-300 leading-snug">{check.description}</p>
        {check.matched_term && (
          <p className="mt-0.5 text-[11px] text-slate-500">
            matched: <code className="text-slate-400">"{check.matched_term}"</code>
          </p>
        )}
      </div>
    </motion.li>
  )
}

function ScoreRing({ passed, total }) {
  const pct = total > 0 ? Math.round((passed / total) * 100) : 0
  const color =
    pct === 100
      ? 'text-emerald-400'
      : pct >= 70
      ? 'text-amber-400'
      : 'text-rose-400'

  return (
    <div className="flex flex-col items-center">
      <span className={`text-3xl font-bold tabular-nums ${color}`}>
        {passed}/{total}
      </span>
      <span className="text-xs text-slate-500 mt-0.5">checks passed</span>
    </div>
  )
}

function EvalResult({ result }) {
  return (
    <motion.div
      key={result.scenario_id}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: 'easeOut' }}
      className="mt-5 space-y-4"
    >
      {/* summary row */}
      <div className="flex items-center justify-between flex-wrap gap-3 rounded-xl border border-slate-700 bg-slate-800/50 px-4 py-3">
        <PassFailBadge passed={result.passed} />
        <ScoreRing passed={result.passed_count} total={result.total_count} />
        <div className="flex flex-col items-end gap-0.5">
          <span className="text-xs text-slate-500">Duration</span>
          <span className="text-sm font-mono text-slate-300">{formatDuration(result.duration_ms)}</span>
        </div>
      </div>

      {/* checks list */}
      <div>
        <p className="mb-1 px-1 text-xs font-semibold uppercase tracking-widest text-slate-500">
          Check Results
        </p>
        <ul className="space-y-0.5">
          {result.checks.map((check, i) => (
            <CheckItem key={check.id} check={check} index={i} />
          ))}
        </ul>
      </div>

      {/* agent answer preview */}
      {result.agent_answer_preview && (
        <div className="rounded-lg border border-slate-700 bg-slate-900 p-3">
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-slate-500">
            Agent Response Preview
          </p>
          <p className="text-xs text-slate-400 leading-relaxed line-clamp-4">
            {result.agent_answer_preview}
          </p>
        </div>
      )}
    </motion.div>
  )
}

// ─── scenario card ───────────────────────────────────────────────────────────

const SCENARIO_META = {
  crisis: {
    icon: AlertTriangle,
    iconColor: 'text-rose-400',
    borderColor: 'border-rose-800/60',
    accentBg: 'bg-rose-500/10',
    glowClass: 'shadow-rose-900/30',
    buttonClass:
      'bg-rose-600 hover:bg-rose-500 focus-visible:ring-rose-500 disabled:bg-rose-900/40 disabled:text-rose-600',
  },
  healthy: {
    icon: Zap,
    iconColor: 'text-emerald-400',
    borderColor: 'border-emerald-800/60',
    accentBg: 'bg-emerald-500/10',
    glowClass: 'shadow-emerald-900/30',
    buttonClass:
      'bg-emerald-600 hover:bg-emerald-500 focus-visible:ring-emerald-500 disabled:bg-emerald-900/40 disabled:text-emerald-600',
  },
}

function ScenarioCard({ scenario, isRunning, result, onRun }) {
  const key = scenario?.id ?? 'unknown'
  const meta = SCENARIO_META[key] ?? SCENARIO_META.crisis
  const Icon = meta.icon

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="flex-1 min-w-0"
    >
      <Card
        className={`h-full border ${meta.borderColor} bg-slate-900 shadow-lg ${meta.glowClass} flex flex-col`}
      >
        {/* card header */}
        <div className={`rounded-t-xl ${meta.accentBg} border-b ${meta.borderColor} px-5 py-4`}>
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <span className={`${meta.iconColor}`}>
                <Icon className="h-5 w-5" />
              </span>
              <div>
                <h3 className="text-base font-semibold text-white leading-tight">
                  {scenario?.name ?? key.toUpperCase()}
                </h3>
                <p className="mt-0.5 text-xs text-slate-400 leading-snug max-w-xs">
                  {scenario?.description ?? 'No description available.'}
                </p>
              </div>
            </div>

            {/* run button */}
            <button
              onClick={() => onRun(scenario.id)}
              disabled={isRunning}
              className={`
                inline-flex shrink-0 items-center gap-1.5 rounded-lg px-3.5 py-2 text-sm font-semibold
                text-white transition-all duration-150 focus:outline-none focus-visible:ring-2
                focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900
                disabled:cursor-not-allowed ${meta.buttonClass}
              `}
            >
              {isRunning ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Running…
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Run Eval
                </>
              )}
            </button>
          </div>
        </div>

        {/* card body */}
        <div className="flex-1 overflow-y-auto px-5 pb-5">
          <AnimatePresence mode="wait">
            {isRunning && !result && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center gap-3 py-12 text-slate-500"
              >
                <Loader2 className="h-8 w-8 animate-spin text-slate-400" />
                <p className="text-sm">Running evaluation scenario…</p>
                <p className="text-xs text-slate-600">This may take up to a minute</p>
              </motion.div>
            )}

            {!isRunning && !result && (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center justify-center gap-2 py-12 text-slate-600"
              >
                <FlaskConical className="h-8 w-8" />
                <p className="text-sm">No results yet</p>
                <p className="text-xs">Click "Run Eval" to start</p>
              </motion.div>
            )}

            {result && !isRunning && (
              <motion.div
                key="result"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <EvalResult result={result} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </Card>
    </motion.div>
  )
}

// ─── page ────────────────────────────────────────────────────────────────────

export default function Evals() {
  const [scenarios, setScenarios] = useState([])
  const [scenariosLoading, setScenariosLoading] = useState(true)
  const [scenariosError, setScenariosError] = useState(null)

  // per-scenario running state: { [scenario_id]: boolean }
  const [running, setRunning] = useState({})
  // per-scenario results: { [scenario_id]: result }
  const [results, setResults] = useState({})
  // per-scenario errors: { [scenario_id]: string }
  const [runErrors, setRunErrors] = useState({})

  // fetch scenarios on mount
  useEffect(() => {
    setScenariosLoading(true)
    setScenariosError(null)
    fetch('/api/evals/scenarios')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => {
        setScenarios(data.scenarios ?? [])
      })
      .catch((err) => {
        setScenariosError(err.message)
      })
      .finally(() => setScenariosLoading(false))
  }, [])

  async function handleRun(scenarioId) {
    setRunning((prev) => ({ ...prev, [scenarioId]: true }))
    setRunErrors((prev) => ({ ...prev, [scenarioId]: null }))

    try {
      const res = await fetch(`/api/evals/run/${scenarioId}`, { method: 'POST' })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      setResults((prev) => ({ ...prev, [scenarioId]: data }))
    } catch (err) {
      setRunErrors((prev) => ({ ...prev, [scenarioId]: err.message }))
    } finally {
      setRunning((prev) => ({ ...prev, [scenarioId]: false }))
    }
  }

  // build an ordered list: crisis first, healthy second, then anything else
  const orderedScenarios = [
    ...(scenarios.filter((s) => s.id === 'crisis')),
    ...(scenarios.filter((s) => s.id === 'healthy')),
    ...(scenarios.filter((s) => s.id !== 'crisis' && s.id !== 'healthy')),
  ]

  // ── render ──────────────────────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-slate-950 px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl space-y-8">

        {/* ── page header ── */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex items-start justify-between flex-wrap gap-4"
        >
          <div>
            <div className="flex items-center gap-2.5 mb-1">
              <FlaskConical className="h-6 w-6 text-primary-400" />
              <h1 className="text-2xl font-bold text-white">Agent Evaluations</h1>
            </div>
            <p className="text-slate-400 text-sm">
              Validate agent intelligence against controlled scenarios
            </p>
          </div>

          {/* aggregate badge — shown only when at least one result exists */}
          {Object.keys(results).length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-800/60 px-4 py-2.5"
            >
              <CheckCircle className="h-4 w-4 text-slate-400" />
              <span className="text-sm text-slate-300">
                {Object.values(results).filter((r) => r.passed).length} /{' '}
                {Object.keys(results).length} scenarios passing
              </span>
            </motion.div>
          )}
        </motion.div>

        {/* ── loading / error states for scenario list ── */}
        <AnimatePresence>
          {scenariosLoading && (
            <motion.div
              key="sl"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center justify-center gap-3 py-24 text-slate-500"
            >
              <Loader2 className="h-6 w-6 animate-spin" />
              <span className="text-sm">Loading scenarios…</span>
            </motion.div>
          )}

          {scenariosError && !scenariosLoading && (
            <motion.div
              key="se"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="rounded-xl border border-rose-800/50 bg-rose-950/40 px-5 py-4 text-rose-400 text-sm flex items-center gap-2"
            >
              <XCircle className="h-4 w-4 shrink-0" />
              Failed to load scenarios: {scenariosError}
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── scenario cards grid ── */}
        {!scenariosLoading && !scenariosError && (
          <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
            {orderedScenarios.map((scenario) => (
              <ScenarioCard
                key={scenario.id}
                scenario={scenario}
                isRunning={!!running[scenario.id]}
                result={results[scenario.id] ?? null}
                onRun={handleRun}
              />
            ))}

            {orderedScenarios.length === 0 && (
              <div className="flex-1 flex flex-col items-center justify-center gap-3 py-24 text-slate-600">
                <FlaskConical className="h-10 w-10" />
                <p className="text-sm">No evaluation scenarios available.</p>
              </div>
            )}
          </div>
        )}

        {/* ── per-scenario run errors ── */}
        <AnimatePresence>
          {Object.entries(runErrors)
            .filter(([, err]) => err)
            .map(([id, err]) => (
              <motion.div
                key={id}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="rounded-xl border border-rose-800/50 bg-rose-950/40 px-5 py-3 text-rose-400 text-sm flex items-center gap-2"
              >
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span>
                  <strong>{id}</strong>: {err}
                </span>
              </motion.div>
            ))}
        </AnimatePresence>

        {/* ── footer note ── */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-xs text-slate-700 pb-2"
        >
          Evaluations run the live AI agent against pre-defined factory state snapshots and score its responses.
        </motion.p>
      </div>
    </div>
  )
}
