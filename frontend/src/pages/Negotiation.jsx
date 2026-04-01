import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import Card, { CardContent, CardHeader } from '../components/Card'
import {
  Play, AlertTriangle, CheckCircle, Clock, TrendingUp, Package,
  Wrench, DollarSign, ChevronDown, ChevronUp, Zap, ArrowRight,
  Terminal, MessageSquare, Eye, EyeOff,
} from 'lucide-react'
import { apiClient } from '../lib/api'

// ── Markdown renderer for agent message previews ─────────────────
const msgMarkdown = {
  h1: ({ children }) => <h1 className="text-sm font-bold text-white mt-3 mb-1.5 first:mt-0">{children}</h1>,
  h2: ({ children }) => <h2 className="text-xs font-bold text-slate-200 mt-2.5 mb-1 first:mt-0 uppercase tracking-wide">{children}</h2>,
  h3: ({ children }) => <h3 className="text-xs font-semibold text-slate-300 mt-2 mb-1 first:mt-0">{children}</h3>,
  p: ({ children }) => <p className="text-xs text-slate-300 leading-relaxed mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-bold text-white">{children}</strong>,
  em: ({ children }) => <em className="italic text-slate-400">{children}</em>,
  ul: ({ children }) => <ul className="space-y-1 mb-2 ml-0.5">{children}</ul>,
  ol: ({ children }) => <ol className="space-y-1 mb-2 ml-0.5 list-none">{children}</ol>,
  li: ({ children }) => (
    <li className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed">
      <span className="mt-1.5 h-1 w-1 rounded-full bg-slate-500 shrink-0" />
      <span className="flex-1">{children}</span>
    </li>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-slate-600 pl-3 py-0.5 my-1.5 text-slate-400 italic text-xs">{children}</blockquote>
  ),
  code: ({ inline, children }) =>
    inline ? (
      <code className="px-1 py-0.5 rounded bg-slate-700 text-slate-300 font-mono text-[10px]">{children}</code>
    ) : (
      <pre className="bg-slate-800 border border-slate-700 rounded p-2 overflow-x-auto my-1.5">
        <code className="text-[10px] font-mono text-slate-300">{children}</code>
      </pre>
    ),
  hr: () => <hr className="border-slate-700 my-2" />,
}

// ── Agent colour palette ──────────────────────────────────────────
const AGENT_STYLES = {
  blue:    { bg: 'bg-blue-600',    ring: 'ring-blue-300',    pill: 'bg-blue-500/10 border border-blue-500/20 text-blue-400',    section: 'border-blue-500/20 bg-blue-500/5',    label: 'text-blue-400' },
  purple:  { bg: 'bg-purple-600',  ring: 'ring-purple-300',  pill: 'bg-violet-500/10 border border-violet-500/20 text-violet-400',  section: 'border-violet-500/20 bg-violet-500/5',  label: 'text-violet-400' },
  emerald: { bg: 'bg-emerald-600', ring: 'ring-emerald-300', pill: 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400', section: 'border-emerald-500/20 bg-emerald-500/5', label: 'text-emerald-400' },
  amber:   { bg: 'bg-amber-500',   ring: 'ring-amber-300',   pill: 'bg-amber-500/10 border border-amber-500/20 text-amber-400',   section: 'border-amber-500/20 bg-amber-500/5',   label: 'text-amber-400' },
  orange:  { bg: 'bg-orange-500',  ring: 'ring-orange-300',  pill: 'bg-orange-500/10 border border-orange-500/20 text-orange-400',  section: 'border-orange-500/20 bg-orange-500/5',  label: 'text-orange-400' },
  gray:    { bg: 'bg-slate-8000',    ring: 'ring-gray-300',    pill: 'bg-slate-800 border border-slate-800 text-slate-300',    section: 'border-slate-800 bg-slate-800/60',    label: 'text-slate-300' },
}

const ROUND_META = {
  1: { label: 'Round 1 · Initial Proposals',  dot: 'bg-blue-500',    text: 'text-blue-400',    bg: 'bg-blue-500/10'    },
  2: { label: 'Round 2 · Agent Critiques',    dot: 'bg-purple-500',  text: 'text-violet-400',  bg: 'bg-violet-500/10'  },
  3: { label: 'Round 3 · Consensus',          dot: 'bg-emerald-500', text: 'text-emerald-400', bg: 'bg-emerald-500/10' },
}

// Shorten noisy tool names to readable tokens
function shortTool(name) {
  const MAP = {
    get_demand_data_summary: 'demand_data',
    simulate_demand_scenarios: 'scenarios',
    analyze_demand_trends: 'trends',
    detect_demand_anomalies: 'anomalies',
    monte_carlo_profit_simulation: 'monte_carlo',
    compare_production_strategies: 'strategies',
    get_inventory_status: 'inventory_status',
    calculate_reorder_point: 'reorder_point',
    optimize_safety_stock: 'safety_stock',
    simulate_stockout_risk: 'stockout_risk',
    evaluate_holding_costs: 'holding_costs',
    generate_replenishment_plan: 'replenishment',
    get_production_context: 'prod_context',
    build_master_production_schedule: 'build_mps',
    analyze_production_bottlenecks: 'bottlenecks',
    evaluate_capacity_gap: 'capacity_gap',
    optimize_production_mix: 'prod_mix',
    generate_production_requirements: 'requirements',
    get_machine_fleet_status: 'fleet_status',
    analyze_sensor_readings: 'sensors',
    predict_failure_risk: 'failure_risk',
    calculate_oee: 'oee',
    generate_maintenance_schedule: 'maint_sched',
    assess_production_capacity_impact: 'capacity_impact',
    get_procurement_context: 'procurement_ctx',
    evaluate_supplier_options: 'suppliers',
    generate_purchase_orders: 'gen_pos',
    assess_supply_chain_risk: 'supply_risk',
    simulate_delivery_risk: 'delivery_risk',
    optimize_supplier_allocation: 'supplier_alloc',
  }
  return MAP[name] || name
}

// ── Execution Trace Panel ─────────────────────────────────────────
function AgentExecutionTrace({ trace, visibleCount }) {
  const [showTrace, setShowTrace] = useState(true)

  if (!trace || trace.length === 0) return null

  const visible = trace.slice(0, visibleCount)
  const totalTools = trace.reduce((s, e) => s + (e.tool_calls?.length || 0), 0)
  const totalMs = trace.reduce((s, e) => s + (e.duration_ms || 0), 0)

  // Group visible events by round
  const rounds = visible.reduce((acc, ev) => {
    if (!acc[ev.round]) acc[ev.round] = []
    acc[ev.round].push(ev)
    return acc
  }, {})

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card className="border-slate-700 overflow-hidden">
        {/* Header */}
        <button
          onClick={() => setShowTrace(v => !v)}
          className="w-full flex items-center justify-between px-6 py-4 hover:bg-slate-800/50 transition-colors"
        >
          <div className="flex items-center gap-3">
            {showTrace ? <EyeOff className="h-5 w-5 text-indigo-500" /> : <Eye className="h-5 w-5 text-indigo-500" />}
            <div className="text-left">
              <p className="text-sm font-semibold text-white">
                Behind the Scenes — Agent Execution Trace
              </p>
              <p className="text-xs text-slate-500">
                {trace.length} agent actions · {totalTools} tool calls · {(totalMs / 1000).toFixed(1)}s total
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="hidden sm:inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-indigo-50 border border-indigo-200 text-xs font-semibold text-indigo-700">
              <Zap className="h-3 w-3" /> Live AI Execution
            </span>
            {showTrace ? <ChevronUp className="h-4 w-4 text-slate-500" /> : <ChevronDown className="h-4 w-4 text-slate-500" />}
          </div>
        </button>

        <AnimatePresence initial={false}>
          {showTrace && (
            <motion.div
              key="trace-body"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="px-6 pb-6 space-y-6 border-t border-gray-100">
                {Object.entries(rounds).map(([roundNum, events]) => {
                  const rm = ROUND_META[parseInt(roundNum)] || ROUND_META[1]
                  return (
                    <div key={roundNum}>
                      {/* Round header */}
                      <div className="flex items-center gap-3 mt-5 mb-3">
                        <span className={`inline-block h-2.5 w-2.5 rounded-full ${rm.dot}`} />
                        <span className={`text-xs font-bold uppercase tracking-widest ${rm.text}`}>
                          {rm.label}
                        </span>
                        <div className="flex-1 h-px bg-slate-700" />
                        <span className="text-xs text-slate-500">{events.length} agents</span>
                      </div>

                      {/* Event cards */}
                      <div className="space-y-3">
                        {events.map((ev, i) => {
                          const s = AGENT_STYLES[ev.agent_color] || AGENT_STYLES.gray
                          return (
                            <motion.div
                              key={ev.seq}
                              initial={{ opacity: 0, x: -12 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ duration: 0.35, delay: i * 0.05 }}
                              className={`rounded-xl border p-4 ${s.section}`}
                            >
                              {/* Agent header row */}
                              <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-3">
                                  {/* Avatar */}
                                  <div className={`h-8 w-8 rounded-full ${s.bg} flex items-center justify-center ring-2 ${s.ring} flex-shrink-0`}>
                                    <span className="text-white text-[10px] font-bold">{ev.agent_initials}</span>
                                  </div>
                                  <div>
                                    <p className={`text-sm font-semibold ${s.label}`}>{ev.agent_label}</p>
                                    {ev.action === 'critique' && ev.addressing?.length > 0 && (
                                      <p className="text-[10px] text-slate-500 flex items-center gap-1">
                                        <ArrowRight className="h-3 w-3" />
                                        addressing: {ev.addressing.join(', ')}
                                      </p>
                                    )}
                                    {ev.action === 'synthesize' && (
                                      <p className="text-[10px] text-slate-500">synthesising all proposals</p>
                                    )}
                                  </div>
                                </div>
                                <div className="flex items-center gap-2 flex-shrink-0">
                                  {ev.duration_ms > 0 && (
                                    <span className="text-[10px] text-slate-500 font-mono">
                                      {(ev.duration_ms / 1000).toFixed(1)}s
                                    </span>
                                  )}
                                  <span className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full ${rm.bg} ${rm.text}`}>
                                    {ev.action}
                                  </span>
                                </div>
                              </div>

                              {/* Tool calls */}
                              {ev.tool_calls?.length > 0 ? (
                                <div className="mb-3">
                                  <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-widest mb-1.5 flex items-center gap-1">
                                    <Terminal className="h-3 w-3" /> Tools called ({ev.tool_calls.length})
                                  </p>
                                  <div className="flex flex-wrap gap-1.5">
                                    {ev.tool_calls.map((tc) => (
                                      <span
                                        key={tc.order}
                                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-mono font-medium ${s.pill}`}
                                      >
                                        <span className="opacity-60">{tc.order}→</span>
                                        {shortTool(tc.name)}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              ) : (
                                <div className="mb-3">
                                  <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-widest mb-1.5 flex items-center gap-1">
                                    <Terminal className="h-3 w-3" /> Tools called
                                  </p>
                                  <span className="text-[10px] text-slate-500 italic">responded from context (no tools needed)</span>
                                </div>
                              )}

                              {/* Message preview */}
                              {ev.message_preview && (
                                <div className="border-t border-white/10 pt-2.5">
                                  <p className="text-[10px] text-slate-500 font-semibold uppercase tracking-widest mb-2 flex items-center gap-1">
                                    <MessageSquare className="h-3 w-3" />
                                    {ev.action === 'propose' ? 'Proposal' : ev.action === 'critique' ? 'Critique' : 'Decision'}
                                  </p>
                                  <div className="bg-slate-800/60 rounded-lg px-3 py-2.5 border border-slate-700/50">
                                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={msgMarkdown}>
                                      {ev.message_preview}
                                    </ReactMarkdown>
                                  </div>
                                </div>
                              )}
                            </motion.div>
                          )
                        })}
                      </div>
                    </div>
                  )
                })}

                {/* Animated cursor while more events are coming */}
                {visibleCount < trace.length && (
                  <motion.div
                    animate={{ opacity: [1, 0.3, 1] }}
                    transition={{ repeat: Infinity, duration: 0.9 }}
                    className="flex items-center gap-2 text-xs text-indigo-500 font-mono"
                  >
                    <span className="h-2 w-2 rounded-full bg-indigo-500 inline-block" />
                    agents processing…
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  )
}

// ── Live Progress (while negotiation is running) ──────────────────
function NegotiationLiveProgress({ currentStep }) {
  const steps = [
    { id: 1, label: 'Round 1 · Each agent independently proposes a solution', agents: ['DA', 'IA', 'PA'] },
    { id: 2, label: 'Round 2 · Agents critique each other\'s proposals',       agents: ['DA', 'IA', 'PA'] },
    { id: 3, label: 'Round 3 · Orchestrator builds consensus decision',         agents: ['OR'] },
  ]

  return (
    <Card className="mb-6 border-indigo-500/20 bg-indigo-500/5">
      <CardHeader>
        <div className="flex items-center gap-2">
          <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}>
            <Zap className="h-5 w-5 text-indigo-600" />
          </motion.div>
          <h2 className="text-base font-semibold text-indigo-300">Agents Negotiating…</h2>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {steps.map((step) => {
            const done    = currentStep > step.id
            const running = currentStep === step.id
            return (
              <div key={step.id} className={`flex items-start gap-3 transition-opacity duration-500 ${currentStep >= step.id ? 'opacity-100' : 'opacity-30'}`}>
                <div className="flex-shrink-0 mt-0.5">
                  {done ? (
                    <CheckCircle className="h-5 w-5 text-emerald-600" />
                  ) : running ? (
                    <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                      <Clock className="h-5 w-5 text-indigo-600" />
                    </motion.div>
                  ) : (
                    <div className="h-5 w-5 rounded-full border-2 border-slate-700" />
                  )}
                </div>
                <div className="flex-1">
                  <p className={`text-sm font-medium ${done ? 'text-slate-500 line-through' : running ? 'text-indigo-300' : 'text-slate-500'}`}>
                    {step.label}
                  </p>
                  {running && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="mt-1.5 flex gap-1.5"
                    >
                      {step.agents.map((a) => (
                        <motion.span
                          key={a}
                          animate={{ opacity: [0.4, 1, 0.4] }}
                          transition={{ repeat: Infinity, duration: 1.4, delay: step.agents.indexOf(a) * 0.3 }}
                          className="px-2 py-0.5 text-[10px] font-bold bg-indigo-500/10 text-indigo-400 rounded-full"
                        >
                          {a}
                        </motion.span>
                      ))}
                    </motion.div>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

// ── Main Page ─────────────────────────────────────────────────────
export default function Negotiation() {
  const [selectedScenario, setSelectedScenario] = useState('demand_spike')
  const [negotiating, setNegotiating]           = useState(false)
  const [result, setResult]                     = useState(null)
  const [currentStep, setCurrentStep]           = useState(0)
  const [visibleCount, setVisibleCount]         = useState(0)
  const [error, setError]                       = useState(null)
  const replayTimer = useRef(null)

  const scenarios = {
    demand_spike: {
      title: 'Demand Spike Crisis',
      icon: TrendingUp,
      description: 'Customer emergency order exceeds normal production capacity',
      details: { customerOrder: 2000, timelineDays: 3, normalCapacity: 1500, gap: 500 },
      color: 'blue',
    },
    supplier_failure: {
      title: 'Supplier Failure',
      icon: Package,
      description: 'Primary supplier cannot deliver critical components',
      details: { missingComponents: 500, productionImpact: '5 days', alternativesAvailable: 2, costPremium: '25%' },
      color: 'orange',
    },
    machine_breakdown: {
      title: 'Machine Breakdown',
      icon: Wrench,
      description: 'Critical manufacturing equipment has failed',
      details: { machineId: 'MCH-004', repairTime: '5 days', repairCost: '$40,000', alternativeCapacity: '60%' },
      color: 'red',
    },
    cost_pressure: {
      title: 'Cost Reduction Pressure',
      icon: DollarSign,
      description: 'Need to reduce costs by 15% while maintaining quality',
      details: { targetReduction: '15%', currentCost: '$50/unit', qualityMustMaintain: true, volumeUnchanged: true },
      color: 'green',
    },
  }

  const colorClasses = {
    blue:   { border: 'border-blue-200',   bg: 'bg-blue-500/10',   text: 'text-blue-900',   badge: 'bg-blue-100 text-blue-800',   btn: '#2563eb' },
    orange: { border: 'border-orange-200', bg: 'bg-orange-500/10', text: 'text-orange-300', badge: 'bg-orange-500/10 text-orange-300', btn: '#ea580c' },
    red:    { border: 'border-red-200',    bg: 'bg-red-500/10', text: 'text-red-300', badge: 'bg-red-500/10 text-red-300',    btn: '#dc2626' },
    green:  { border: 'border-green-200',  bg: 'bg-emerald-500/10', text: 'text-emerald-300', badge: 'bg-emerald-500/10 text-emerald-300',  btn: '#16a34a' },
  }

  // Step timer while negotiating
  useEffect(() => {
    if (!negotiating) return
    const t1 = setTimeout(() => setCurrentStep(1), 600)
    const t2 = setTimeout(() => setCurrentStep(2), 12000)
    const t3 = setTimeout(() => setCurrentStep(3), 22000)
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
  }, [negotiating])

  // Replay animation: reveal trace events one by one after result arrives
  useEffect(() => {
    if (!result?.execution_trace?.length) return
    setVisibleCount(0)
    let idx = 0
    replayTimer.current = setInterval(() => {
      idx += 1
      setVisibleCount(idx)
      if (idx >= result.execution_trace.length) clearInterval(replayTimer.current)
    }, 700)
    return () => clearInterval(replayTimer.current)
  }, [result])

  const runNegotiation = async () => {
    setNegotiating(true)
    setResult(null)
    setError(null)
    setCurrentStep(0)
    setVisibleCount(0)
    clearInterval(replayTimer.current)

    try {
      const sc = scenarios[selectedScenario]
      const response = await apiClient.runNegotiation(
        selectedScenario,
        'PROD-A',
        sc.details.customerOrder || 2000,
        sc.details.timelineDays  || 3,
      )
      setResult(response.data.result)
      setCurrentStep(4)
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Negotiation failed')
    } finally {
      setNegotiating(false)
    }
  }

  const sc    = scenarios[selectedScenario]
  const ScIcon = sc.icon
  const cls   = colorClasses[sc.color]

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-white">Agent Negotiation System</h1>
        <p className="mt-1 text-sm text-slate-500">
          Watch specialised AI agents debate manufacturing decisions in real time and reach consensus
        </p>
      </div>

      {/* Scenario cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {Object.entries(scenarios).map(([key, s]) => {
          const Icon      = s.icon
          const isSelected = selectedScenario === key
          const c         = colorClasses[s.color]
          return (
            <button
              key={key}
              onClick={() => setSelectedScenario(key)}
              disabled={negotiating}
              className={`p-4 rounded-xl border-2 transition-all text-left ${
                isSelected ? `${c.border} ${c.bg} shadow-md` : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
              } ${negotiating ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <Icon className={`h-5 w-5 ${isSelected ? c.text : 'text-slate-500'}`} />
                <span className={`font-semibold text-sm ${isSelected ? c.text : 'text-white'}`}>{s.title}</span>
              </div>
              <p className="text-xs text-slate-500">{s.description}</p>
            </button>
          )
        })}
      </div>

      {/* Selected scenario details + run button */}
      <Card className={`${cls.border} ${cls.bg}`}>
        <CardHeader>
          <div className="flex items-center gap-3">
            <ScIcon className={`h-6 w-6 ${cls.text}`} />
            <h2 className="text-lg font-bold">{sc.title}</h2>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
            {Object.entries(sc.details).map(([k, v]) => (
              <div key={k} className="bg-slate-700/50 p-3 rounded-lg">
                <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mb-1">
                  {k.replace(/([A-Z])/g, ' $1').trim()}
                </div>
                <div className="font-semibold text-sm text-white">
                  {typeof v === 'boolean' ? (v ? '✓ Yes' : '✗ No') : v}
                </div>
              </div>
            ))}
          </div>
          <button
            onClick={runNegotiation}
            disabled={negotiating}
            className="px-6 py-2.5 rounded-lg font-semibold flex items-center gap-2 text-white transition-opacity disabled:opacity-60"
            style={{ backgroundColor: cls.btn }}
          >
            {negotiating ? (
              <>
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                  <Clock className="h-4 w-4" />
                </motion.div>
                Agents Negotiating…
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Start Agent Negotiation
              </>
            )}
          </button>
        </CardContent>
      </Card>

      {/* Live progress while running */}
      {negotiating && <NegotiationLiveProgress currentStep={currentStep} />}

      {/* Error */}
      {error && (
        <Card className="border-red-500/20 bg-red-500/10">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-red-300">Negotiation Failed</h3>
                <p className="text-sm text-red-400 mt-1">{error}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Execution Trace — appears after result */}
      {result && (
        <AgentExecutionTrace
          trace={result.execution_trace}
          visibleCount={visibleCount}
        />
      )}

      {/* Consensus result card */}
      {result && (
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}>
          <Card className="border-emerald-500/20 bg-emerald-500/10">
            <CardHeader>
              <div className="flex items-center gap-2">
                <CheckCircle className="h-6 w-6 text-emerald-600" />
                <h2 className="text-lg font-bold text-emerald-300">Consensus Reached</h2>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {result.round_3_consensus?.final_decision && (
                  <div className="bg-slate-800 rounded-xl p-4 border border-emerald-500/20">
                    <h3 className="text-xs font-bold uppercase tracking-widest text-emerald-400 mb-2">Final Decision</h3>
                    <div>
                      <ReactMarkdown remarkPlugins={[remarkGfm]} components={msgMarkdown}>
                        {typeof result.round_3_consensus.final_decision === 'string'
                          ? result.round_3_consensus.final_decision
                          : JSON.stringify(result.round_3_consensus.final_decision, null, 2)}
                      </ReactMarkdown>
                    </div>
                  </div>
                )}

                {/* Agent badges — derived from actual execution trace */}
                <div className="bg-slate-800 rounded-xl p-4 border border-emerald-500/20">
                  <h3 className="text-xs font-bold uppercase tracking-widest text-emerald-400 mb-3">Agents that contributed</h3>
                  <div className="flex flex-wrap gap-2">
                    {(result.execution_trace || [])
                      .filter(ev => ev.round === 1)
                      .map(ev => {
                        const s = AGENT_STYLES[ev.agent_color] || AGENT_STYLES.gray
                        return (
                          <span key={ev.agent} className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${s.pill}`}>
                            <span className={`h-2 w-2 rounded-full ${s.bg}`} />
                            {ev.agent_label}
                          </span>
                        )
                      })}
                  </div>
                  <p className="text-xs text-slate-500 mt-3">
                    {result.round_3_consensus?.agents_involved || (result.execution_trace?.filter(e => e.round === 1).length ?? 0)} agents · 3 rounds · consensus achieved
                  </p>
                </div>

                <p className="text-xs text-slate-500">
                  Completed: {new Date(result.timestamp).toLocaleString()}
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}
