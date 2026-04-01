import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ChevronLeft, ChevronRight, Menu, X, TrendingUp, Package,
  Cpu, Truck, CheckCircle, XCircle, AlertTriangle, Zap,
  Globe, Shield, BarChart3, ArrowRight, Clock, DollarSign,
  Star, RefreshCw, Target, Brain, Database, Layers,
  MessageSquare, Play, Factory, Users,
} from 'lucide-react'

// ─── Slide metadata ────────────────────────────────────────────────────────────

const SLIDES_META = [
  { title: 'AMIS',                       label: 'Introduction' },
  { title: 'The Problem',                label: 'Problem Statement' },
  { title: 'Before AMIS',               label: 'Current State' },
  { title: 'After AMIS',                label: 'Transformation' },
  { title: 'What is AMIS?',             label: 'Solution Overview' },
  { title: 'AI Agents',                 label: '5 Specialist Agents' },
  { title: 'Demand Forecasting Agent',  label: 'Agent Deep Dive — 6 Tools' },
  { title: 'Inventory Management Agent',label: 'Agent Deep Dive — 6 Tools' },
  { title: 'Machine Health Agent',      label: 'Agent Deep Dive — 6 Tools' },
  { title: 'Production Planning Agent', label: 'Agent Deep Dive — 6 Tools' },
  { title: 'Supplier Procurement Agent',label: 'Agent Deep Dive — 6 Tools' },
  { title: 'How It Works',              label: 'System Flow' },
  { title: 'Agent Negotiation',         label: 'Crisis Resolution' },
  { title: 'Impact & ROI',              label: 'Real Results' },
  { title: 'Future Vision',             label: 'SaaS Roadmap' },
]

// ─── Animation variants ────────────────────────────────────────────────────────

const slideVariants = {
  enter:  (dir) => ({ x: dir > 0 ? '100%' : '-100%', opacity: 0, scale: 0.97 }),
  center: { x: 0, opacity: 1, scale: 1, transition: { duration: 0.48, ease: [0.25, 0.46, 0.45, 0.94] } },
  exit:   (dir) => ({ x: dir > 0 ? '-100%' : '100%', opacity: 0, scale: 0.97, transition: { duration: 0.38, ease: [0.25, 0.46, 0.45, 0.94] } }),
}

const fadeUp = { hidden: { opacity: 0, y: 22 }, show: { opacity: 1, y: 0, transition: { duration: 0.5 } } }
const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.09, delayChildren: 0.05 } } }

// ─── Shared primitives ─────────────────────────────────────────────────────────

function Orbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none select-none">
      <div style={{ position:'absolute', top:'-8%', left:'-6%', width:480, height:480, borderRadius:'50%', background:'radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%)', filter:'blur(40px)' }} />
      <div style={{ position:'absolute', bottom:'-10%', right:'-6%', width:480, height:480, borderRadius:'50%', background:'radial-gradient(circle, rgba(59,130,246,0.16) 0%, transparent 70%)', filter:'blur(40px)' }} />
      <div style={{ position:'absolute', top:'45%', left:'48%', width:300, height:300, borderRadius:'50%', transform:'translate(-50%,-50%)', background:'radial-gradient(circle, rgba(139,92,246,0.10) 0%, transparent 70%)', filter:'blur(40px)' }} />
    </div>
  )
}

function Glass({ children, className = '', accent = false, hover = false }) {
  return (
    <div
      className={[
        'rounded-2xl border backdrop-blur-sm',
        accent  ? 'bg-indigo-600/10 border-indigo-500/30'
                : 'bg-white/[0.03] border-white/[0.08]',
        hover   ? 'transition-all duration-200 hover:bg-white/[0.06] hover:border-white/[0.14]' : '',
        className,
      ].join(' ')}
    >
      {children}
    </div>
  )
}

function Tag({ children, color = 'indigo' }) {
  const map = {
    indigo: 'bg-indigo-600/20 border-indigo-500/30 text-indigo-300',
    emerald:'bg-emerald-600/20 border-emerald-500/30 text-emerald-300',
    red:    'bg-red-600/20 border-red-500/30 text-red-300',
    violet: 'bg-violet-600/20 border-violet-500/30 text-violet-300',
    amber:  'bg-amber-600/20 border-amber-500/30 text-amber-300',
  }
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-xs font-semibold uppercase tracking-widest ${map[color]}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${color === 'indigo' ? 'bg-indigo-400' : color === 'emerald' ? 'bg-emerald-400' : color === 'red' ? 'bg-red-400' : color === 'violet' ? 'bg-violet-400' : 'bg-amber-400'} animate-pulse`} />
      {children}
    </span>
  )
}

function Counter({ to, prefix = '', suffix = '' }) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    let f = 0, total = 72
    const t = setInterval(() => {
      f++
      const ease = 1 - Math.pow(1 - f / total, 3)
      setVal(Math.floor(ease * to))
      if (f >= total) { setVal(to); clearInterval(t) }
    }, 18)
    return () => clearInterval(t)
  }, [to])
  return <>{prefix}{val.toLocaleString()}{suffix}</>
}

function SectionLabel({ children, color = 'text-indigo-400' }) {
  return (
    <motion.p variants={fadeUp} className={`text-xs font-bold uppercase tracking-[0.18em] mb-2 ${color}`}>
      {children}
    </motion.p>
  )
}

function SectionTitle({ children }) {
  return (
    <motion.h2 variants={fadeUp} className="text-4xl md:text-5xl font-extrabold text-white mb-6 leading-tight">
      {children}
    </motion.h2>
  )
}

// ─── Slide 1 — Title ───────────────────────────────────────────────────────────

function SlideTitle({ onNext }) {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10 space-y-7 max-w-3xl mx-auto">

        <motion.div variants={fadeUp}>
          <Tag>AI-Powered Manufacturing Intelligence</Tag>
        </motion.div>

        <motion.div variants={fadeUp}>
          <h1
            className="text-[7rem] md:text-[9rem] font-black tracking-tight leading-none"
            style={{ background: 'linear-gradient(135deg,#fff 0%,#a5b4fc 45%,#60a5fa 100%)', WebkitBackgroundClip:'text', WebkitTextFillColor:'transparent' }}
          >
            AMIS
          </h1>
          <p className="mt-3 text-xl md:text-2xl font-light text-slate-300 tracking-wide">
            Autonomous Manufacturing Intelligence System
          </p>
          <p className="mt-2 text-base text-slate-500 italic">"From reactive chaos to proactive intelligence"</p>
        </motion.div>

        <motion.div variants={fadeUp} className="flex items-center justify-center gap-2 flex-wrap">
          {['Claude Sonnet 4.6', 'FastAPI', 'React + Vite', 'SQLite', 'LangChain'].map(t => (
            <span key={t} className="px-3 py-1 rounded-lg bg-white/5 border border-white/10 text-slate-400 text-xs font-mono">{t}</span>
          ))}
        </motion.div>

        <motion.button
          variants={fadeUp}
          onClick={onNext}
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.97 }}
          className="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-base transition-colors shadow-lg shadow-indigo-600/30"
        >
          <Play className="h-5 w-5" />
          Begin Presentation
        </motion.button>

        <motion.p variants={fadeUp} className="text-xs text-slate-600">
          Use ← → arrow keys or click the buttons to navigate
        </motion.p>
      </motion.div>
    </div>
  )
}

// ─── Slide 2 — Problem Statement ──────────────────────────────────────────────

function SlideProblem() {
  const stats = [
    { to: 260000, prefix: '$', suffix: '/hr', label: 'Average unplanned downtime cost', color: 'text-red-400' },
    { to: 23,     prefix: '',  suffix: '%',   label: 'Inventory wasted industry-wide', color: 'text-amber-400' },
    { to: 4,      prefix: '',  suffix: '+ hrs', label: 'Daily crisis meeting overhead', color: 'text-orange-400' },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel color="text-red-400">The Problem</SectionLabel>
        <SectionTitle>Manufacturing Runs on <span className="text-red-400">Guesswork</span></SectionTitle>

        <motion.div variants={fadeUp} className="mb-7">
          <Glass className="border-l-4 border-l-amber-500 p-5">
            <p className="text-slate-200 text-lg leading-relaxed">
              <span className="text-amber-400 font-bold">Tuesday morning.</span>{' '}
              Your biggest customer needs 2,000 units by Friday. You have parts for only 1,200.
              Supplier shipment is delayed 3 days. Machine #3 is vibrating — nobody knows when it will fail.
              Your production manager is still working from{' '}
              <span className="text-red-400 font-bold">last week's spreadsheet.</span>
            </p>
          </Glass>
        </motion.div>

        <motion.div variants={stagger} className="grid grid-cols-3 gap-4 mb-6">
          {stats.map(({ to, prefix, suffix, label, color }) => (
            <motion.div key={label} variants={fadeUp}>
              <Glass className="text-center p-5">
                <p className={`text-4xl font-black mb-2 ${color}`}>
                  <Counter to={to} prefix={prefix} suffix={suffix} />
                </p>
                <p className="text-slate-400 text-sm">{label}</p>
              </Glass>
            </motion.div>
          ))}
        </motion.div>

        <motion.div variants={stagger} className="grid grid-cols-3 gap-3">
          {[
            { icon: AlertTriangle, text: "Decisions made from yesterday's data" },
            { icon: XCircle,       text: 'Every department is a silo — no shared intelligence' },
            { icon: Clock,         text: 'Crises managed after they hit — never before' },
          ].map(({ icon: Icon, text }) => (
            <motion.div key={text} variants={fadeUp}
              className="flex items-center gap-3 px-4 py-3 rounded-xl bg-red-950/25 border border-red-900/30">
              <Icon className="h-5 w-5 text-red-400 shrink-0" />
              <span className="text-slate-300 text-sm">{text}</span>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  )
}

// ─── Slide 3 — Before AMIS ────────────────────────────────────────────────────

function SlideBefore() {
  const pains = [
    { icon: XCircle, title: 'Spreadsheet Planning',   desc: "Updated weekly — you're always managing last week's reality" },
    { icon: XCircle, title: 'Reactive Maintenance',   desc: 'Machine fails → emergency repair → 8+ hours of lost production' },
    { icon: XCircle, title: 'Blind Inventory',        desc: 'Stockouts discovered on the day they halt the production line' },
    { icon: XCircle, title: 'Supplier Surprises',     desc: 'Delays discovered on the expected delivery date — far too late' },
    { icon: XCircle, title: 'Gut-Feel Forecasting',   desc: "Demand plan = last year's sales + a hunch. No real trend data." },
    { icon: XCircle, title: 'Siloed Crisis Meetings', desc: "4+ hours daily coordinating departments who can't see each other" },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel color="text-red-400">Before AMIS</SectionLabel>
        <SectionTitle>The Daily Struggle</SectionTitle>

        <motion.div variants={stagger} className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {pains.map(({ icon: Icon, title, desc }) => (
            <motion.div key={title} variants={fadeUp} whileHover={{ y: -3 }} transition={{ type:'spring', stiffness:300 }}>
              <Glass className="p-5 h-full border-red-900/25 hover:border-red-700/40 transition-colors">
                <div className="flex items-start gap-3">
                  <Icon className="h-5 w-5 text-red-400 mt-0.5 shrink-0" />
                  <div>
                    <p className="text-white font-semibold text-sm mb-1">{title}</p>
                    <p className="text-slate-400 text-xs leading-relaxed">{desc}</p>
                  </div>
                </div>
              </Glass>
            </motion.div>
          ))}
        </motion.div>

        <motion.div variants={fadeUp} className="mt-6 p-4 rounded-xl bg-red-950/20 border border-red-900/20 text-center">
          <p className="text-red-300 text-sm font-semibold">
            Result: Factories spend more time fighting fires than preventing them.
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}

// ─── Slide 4 — After AMIS ─────────────────────────────────────────────────────

function SlideAfter() {
  const rows = [
    { icon: RefreshCw, before: 'Excel sheets updated weekly',             after: 'Live dashboard updated every 15 minutes' },
    { icon: Zap,       before: 'Manual phone calls across 3 departments', after: 'AI checks all systems simultaneously, instantly' },
    { icon: Cpu,       before: 'Machine fails → 8-hour emergency repair', after: 'AI predicts failure 72 hrs early → 2 hr planned fix' },
    { icon: Truck,     before: 'Supplier delay found on delivery day',     after: 'AI flags supplier risk 2 weeks in advance' },
    { icon: TrendingUp,before: "Demand forecast = last year's gut feel",   after: 'AI forecasts from 12 weeks of real trend data' },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel color="text-emerald-400">After AMIS</SectionLabel>
        <SectionTitle>The Transformation</SectionTitle>

        <motion.div variants={stagger} className="space-y-3">
          {rows.map(({ icon: Icon, before, after }) => (
            <motion.div key={before} variants={fadeUp} className="grid gap-3 items-center"
              style={{ gridTemplateColumns: '1fr 48px 1fr' }}>
              <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-red-950/20 border border-red-900/20">
                <XCircle className="h-4 w-4 text-red-400 shrink-0" />
                <span className="text-slate-400 text-sm">{before}</span>
              </div>
              <div className="flex items-center justify-center">
                <div className="p-2 rounded-full bg-indigo-600/20 border border-indigo-500/30">
                  <Icon className="h-4 w-4 text-indigo-400" />
                </div>
              </div>
              <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-emerald-950/20 border border-emerald-900/25">
                <CheckCircle className="h-4 w-4 text-emerald-400 shrink-0" />
                <span className="text-emerald-200 text-sm font-medium">{after}</span>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  )
}

// ─── Slide 5 — What is AMIS ───────────────────────────────────────────────────

function SlideWhatIsAMIS() {
  const layers = [
    { icon: Database,     label: 'SENSE', sub: 'Read real factory data', desc: 'Machines, inventory, orders, suppliers — all live and connected', color: 'text-blue-400', ring: 'bg-blue-600/10 border-blue-500/30' },
    { icon: Brain,        label: 'THINK', sub: '5 AI agents analyze',    desc: 'Each agent specializes, then shares insights with all others',  color: 'text-indigo-400', ring: 'bg-indigo-600/10 border-indigo-500/30' },
    { icon: CheckCircle,  label: 'ACT',   sub: 'Manager approves',       desc: 'One-click approval → system executes and logs everything',        color: 'text-emerald-400', ring: 'bg-emerald-600/10 border-emerald-500/30' },
  ]
  const diffs = [
    { icon: Target,  text: 'Not just a dashboard — it recommends concrete decisions',     color: 'text-indigo-400' },
    { icon: Shield,  text: 'Not fully autonomous — the manager always stays in control', color: 'text-emerald-400' },
    { icon: Layers,  text: 'Not siloed — every agent shares intelligence with others',    color: 'text-blue-400' },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel>Solution Overview</SectionLabel>
        <SectionTitle>What is AMIS?</SectionTitle>

        <motion.div variants={fadeUp} className="mb-7">
          <Glass accent className="p-5 text-center">
            <p className="text-xl text-slate-200 leading-relaxed">
              AMIS gives your factory a <span className="text-indigo-300 font-bold">brain</span>.
              Five specialist AI agents watch every corner of your business and talk to each other.
              When something goes wrong, AMIS plans a response and the manager approves it.{' '}
              <span className="text-emerald-400 font-semibold">No more guessing. No more surprises.</span>
            </p>
          </Glass>
        </motion.div>

        <motion.div variants={stagger} className="grid grid-cols-3 gap-5 mb-6">
          {layers.map(({ icon: Icon, label, sub, desc, color, ring }, i) => (
            <motion.div key={label} variants={fadeUp}>
              <Glass className={`text-center p-6 h-full ${ring}`}>
                <div className={`inline-flex p-3 rounded-xl ${ring} mb-3`}>
                  <Icon className={`h-8 w-8 ${color}`} />
                </div>
                <p className={`text-2xl font-black mb-1 ${color}`}>{label}</p>
                <p className="text-white font-semibold text-sm mb-2">{sub}</p>
                <p className="text-slate-400 text-xs leading-relaxed">{desc}</p>
              </Glass>
            </motion.div>
          ))}
        </motion.div>

        <motion.div variants={stagger} className="grid grid-cols-3 gap-3">
          {diffs.map(({ icon: Icon, text, color }) => (
            <motion.div key={text} variants={fadeUp}
              className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
              <Icon className={`h-5 w-5 ${color} shrink-0`} />
              <span className="text-slate-300 text-sm">{text}</span>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  )
}

// ─── Slide 6 — AI Agents ──────────────────────────────────────────────────────

function SlideAgents() {
  const agents = [
    { icon: TrendingUp, name: 'Demand Agent',      color: 'text-blue-400',    ring: 'bg-blue-600/10 border-blue-500/30',
      what: 'Forecasts product demand for the next 12 weeks using historical trend analysis',
      example: 'Demand grew 8%/week → predicts 1,820 units needed in Week 5',
      why: 'Stops overproduction & stockouts before they happen' },
    { icon: Package,    name: 'Inventory Agent',   color: 'text-purple-400',  ring: 'bg-purple-600/10 border-purple-500/30',
      what: 'Monitors real-time stock levels and decides when and how much to reorder',
      example: 'Stock = 215, forecast = 400 → reorder alert raised today, not on the day of shortage',
      why: 'Eliminates expensive emergency orders (30–40% cost premium)' },
    { icon: Cpu,        name: 'Machine Health',    color: 'text-amber-400',   ring: 'bg-amber-600/10 border-amber-500/30',
      what: 'Monitors OEE, vibration and error rates — predicts failures before they cause downtime',
      example: 'OEE drops 87%→71% over 3 days → 68% failure risk → maintenance scheduled before breakdown',
      why: 'Planned maintenance costs 3–4× less than emergency repairs' },
    { icon: Factory,    name: 'Production Agent',  color: 'text-emerald-400', ring: 'bg-emerald-600/10 border-emerald-500/30',
      what: 'Builds a weekly production schedule balancing forecast demand vs. machine capacity',
      example: 'Demand 1,800 / Capacity 1,400 → flags gap → recommends activating overtime shift',
      why: "Stops the classic problem of promising what you can't deliver" },
    { icon: Truck,      name: 'Supplier Agent',    color: 'text-rose-400',    ring: 'bg-rose-600/10 border-rose-500/30',
      what: 'Evaluates every supplier by performance score, on-time delivery, and risk status',
      example: 'Supplier X: 92% on-time. Supplier Y: 61% + 2 delays → route orders to X, flag Y',
      why: 'One unreliable supplier can shut down an entire factory' },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel>The Intelligence Layer</SectionLabel>
        <SectionTitle>5 Specialist AI Agents</SectionTitle>

        <motion.div variants={stagger} className="grid grid-cols-5 gap-3">
          {agents.map(({ icon: Icon, name, color, ring, what, example, why }) => (
            <motion.div key={name} variants={fadeUp}
              whileHover={{ y: -5, scale: 1.02 }}
              transition={{ type:'spring', stiffness:280, damping:20 }}>
              <Glass className={`h-full flex flex-col p-4 ${ring}`}>
                <div className={`inline-flex p-2 rounded-lg ${ring} mb-3 self-start`}>
                  <Icon className={`h-5 w-5 ${color}`} />
                </div>
                <p className={`font-bold text-sm mb-2 ${color}`}>{name}</p>
                <p className="text-slate-300 text-xs mb-3 flex-1 leading-relaxed">{what}</p>
                <div className="p-2 rounded-lg bg-white/[0.04] border border-white/[0.06] mb-2">
                  <p className="text-slate-400 text-[11px] italic leading-relaxed">{example}</p>
                </div>
                <p className="text-[11px] text-slate-500 leading-relaxed">{why}</p>
              </Glass>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  )
}

// ─── Agent Detail — Shared Layout ────────────────────────────────────────────

function AgentDetailSlide({ icon: Icon, name, tagline, color, ring, tagColor, mission, reads, outputs, tools }) {
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">

        <motion.div variants={fadeUp} className="mb-4">
          <Tag color={tagColor}>Agent Deep Dive</Tag>
        </motion.div>

        <div className="grid gap-6" style={{ gridTemplateColumns: '2fr 3fr' }}>

          {/* Left — identity + mission + data flow */}
          <motion.div variants={stagger} className="space-y-3">
            <motion.div variants={fadeUp} className="flex items-center gap-3">
              <div className={`p-3 rounded-xl border ${ring}`}>
                <Icon className={`h-8 w-8 ${color}`} />
              </div>
              <div>
                <h2 className="text-2xl font-extrabold text-white leading-tight">{name}</h2>
                <p className={`text-sm mt-0.5 ${color}`}>{tagline}</p>
              </div>
            </motion.div>

            <motion.div variants={fadeUp}>
              <Glass className="p-4">
                <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">Mission</p>
                <p className="text-slate-300 text-sm leading-relaxed">{mission}</p>
              </Glass>
            </motion.div>

            <motion.div variants={fadeUp}>
              <Glass className="p-4 space-y-3">
                <div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Reads from Database</p>
                  <p className="text-xs text-slate-400 leading-relaxed">{reads}</p>
                </div>
                <div className="border-t border-white/[0.06] pt-3">
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Passes Downstream To Pipeline</p>
                  <p className={`text-xs leading-relaxed ${color}`}>{outputs}</p>
                </div>
              </Glass>
            </motion.div>
          </motion.div>

          {/* Right — tools grid */}
          <motion.div variants={stagger}>
            <motion.p variants={fadeUp} className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">
              {tools.length} LangChain @tool Functions Called
            </motion.p>
            <div className="grid grid-cols-2 gap-2">
              {tools.map((tool, i) => (
                <motion.div key={tool.name} variants={fadeUp}
                  whileHover={{ y: -2 }} transition={{ type: 'spring', stiffness: 300 }}>
                  <Glass className="p-3 h-full hover:border-white/[0.14] transition-colors">
                    <div className="flex items-start gap-2">
                      <span className={`text-xs font-black ${color} shrink-0 font-mono`}>
                        {String(i + 1).padStart(2, '0')}
                      </span>
                      <div>
                        <p className="text-white text-[11px] font-semibold mb-1 font-mono leading-tight">{tool.name}</p>
                        <p className="text-slate-500 text-[11px] leading-relaxed">{tool.desc}</p>
                      </div>
                    </div>
                  </Glass>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}

// ─── Slide 6a — Demand Forecasting Agent ─────────────────────────────────────

function SlideAgentDemand() {
  return <AgentDetailSlide
    icon={TrendingUp}
    name="Demand Forecasting Agent"
    tagline="Predicts what the market will need — before it asks"
    color="text-blue-400"
    ring="bg-blue-600/10 border-blue-500/30"
    tagColor="indigo"
    mission="Analyzes historical sales data, seasonal patterns, and current order pipeline to forecast product demand up to 12 weeks ahead. Produces three probability-weighted scenarios (Optimistic, Base, Pessimistic) so production teams plan for uncertainty — not just averages."
    reads="Demand history records, current inventory levels, open customer orders, production capacity constraints, market context data"
    outputs="12-week demand forecast per scenario, probability weights, anomaly alert flags, recommended weekly production targets passed to the Production Agent"
    tools={[
      { name: 'get_demand_data_summary',       desc: 'First tool always called. Pulls the complete baseline — demand history, inventory, capacity, market context — to ground every subsequent analysis.' },
      { name: 'analyze_demand_trends',          desc: 'Calculates trend direction (up/down/flat), seasonality index, and weekly growth rate from all historical demand records.' },
      { name: 'simulate_demand_scenarios',      desc: 'Generates Optimistic, Base, and Pessimistic forecasts with probability weights for the next 1–12 weeks.' },
      { name: 'monte_carlo_profit_simulation',  desc: 'Runs 1,000+ random simulations to quantify expected profit ranges and financial risk under demand uncertainty.' },
      { name: 'compare_production_strategies',  desc: 'Tests multiple production volume strategies side by side and ranks them by expected profit given forecast uncertainty.' },
      { name: 'detect_demand_anomalies',        desc: 'Flags unusual spikes or drops that fall outside expected statistical ranges — the early-warning system for demand shocks.' },
    ]}
  />
}

// ─── Slide 6b — Inventory Management Agent ────────────────────────────────────

function SlideAgentInventory() {
  return <AgentDetailSlide
    icon={Package}
    name="Inventory Management Agent"
    tagline="Ensures the right stock is in the right place at the right time"
    color="text-purple-400"
    ring="bg-purple-600/10 border-purple-500/30"
    tagColor="violet"
    mission="Monitors real-time stock levels across all warehouse zones, calculates optimal reorder points using safety stock methodology, and generates a week-by-week replenishment plan. Uses Monte Carlo simulation to quantify stockout risk before it becomes a reality."
    reads="Current inventory per product & warehouse zone, open purchase orders in transit, supplier lead times, stockout history, demand forecast from Demand Agent"
    outputs="Reorder alerts with quantities and timing, stockout risk scores, optimal safety stock levels, 4-week replenishment schedule passed to Supplier Agent"
    tools={[
      { name: 'get_inventory_status',         desc: 'First tool called. Gets complete stock picture — current levels, warehouse zone utilization, incoming orders, supplier reliability, and recent stockout history.' },
      { name: 'calculate_reorder_point',      desc: 'Calculates the exact stock level that triggers a replenishment order using demand variability and supplier lead time (service level target: 95%).' },
      { name: 'optimize_safety_stock',        desc: 'Finds the economically optimal safety stock by balancing annual holding cost ($2.30/unit) against stockout cost ($45/unit).' },
      { name: 'simulate_stockout_risk',       desc: 'Runs 1,000 Monte Carlo simulations to calculate the probability of running out of stock within the next N days.' },
      { name: 'evaluate_holding_costs',       desc: 'Calculates the total cost of carrying current inventory vs. the financial risk of being caught short — informs the reorder decision.' },
      { name: 'generate_replenishment_plan',  desc: 'Produces a week-by-week reorder schedule with exact order quantities for the full 4-week planning horizon.' },
    ]}
  />
}

// ─── Slide 6c — Machine Health Agent ─────────────────────────────────────────

function SlideAgentMachine() {
  return <AgentDetailSlide
    icon={Cpu}
    name="Machine Health Agent"
    tagline="Predicts failures before they stop the production line"
    color="text-amber-400"
    ring="bg-amber-600/10 border-amber-500/30"
    tagColor="amber"
    mission="Continuously monitors OEE (Overall Equipment Effectiveness), vibration, temperature, and error rates for every machine. Uses MTBF-based failure probability models and sensor degradation signals to predict breakdowns 72+ hours ahead — when planned maintenance is still possible."
    reads="Machine sensor readings (OEE, vibration, temperature, error rate), historical MTBF records, maintenance work order history, production capacity requirements"
    outputs="Failure risk scores per machine (0–100%), maintenance work order recommendations, real available production capacity figure passed to the Production Agent"
    tools={[
      { name: 'get_machine_fleet_status',           desc: 'First tool called. Returns health score, alert level, and status for every machine in the plant — the starting point for health assessment.' },
      { name: 'analyze_sensor_readings',            desc: 'Compares live sensor data against historical baselines. Calculates % deviation and flags readings that indicate early degradation.' },
      { name: 'predict_failure_risk',               desc: 'Uses exponential failure distribution (MTBF-based) adjusted by current sensor degradation to predict failure probability within N days.' },
      { name: 'calculate_oee',                      desc: 'Computes OEE = Availability × Performance × Quality Rate for each machine. World-class target = 85%. Below 65% = critical.' },
      { name: 'generate_maintenance_schedule',      desc: 'Builds an optimized 14-day maintenance schedule that minimises downtime windows while protecting weekly production targets.' },
      { name: 'assess_production_capacity_impact',  desc: 'Calculates real available capacity after accounting for machines that are down (0%) or degraded (reduced %), giving Production Agent a reliable number.' },
    ]}
  />
}

// ─── Slide 6d — Production Planning Agent ─────────────────────────────────────

function SlideAgentProduction() {
  return <AgentDetailSlide
    icon={Factory}
    name="Production Planning Agent"
    tagline="Turns demand forecasts and machine capacity into a real schedule"
    color="text-emerald-400"
    ring="bg-emerald-600/10 border-emerald-500/30"
    tagColor="emerald"
    mission="Consumes the demand forecast, machine capacity, and current inventory position to build a realistic 4-week Master Production Schedule (MPS). Identifies capacity gaps, pinpoints bottleneck production lines using Theory of Constraints, and generates the Bill of Materials required for each week."
    reads="Demand forecast from Demand Agent, real capacity from Machine Health Agent, current inventory from Inventory Agent, shift configuration, production line specs, BOM data"
    outputs="Master Production Schedule (MPS) with weekly targets, capacity gap analysis, bottleneck identification, component requirements list passed to Supplier Agent"
    tools={[
      { name: 'get_production_context',           desc: 'First tool called. Consolidates machine capacity, inventory position, production history, shift configuration, and product specs into one planning baseline.' },
      { name: 'build_master_production_schedule', desc: 'Builds the 4-week MPS respecting machine downtime windows, maintenance schedules, shift patterns, and capacity constraints.' },
      { name: 'analyze_production_bottlenecks',   desc: 'Uses Theory of Constraints to identify which production line is the system constraint limiting total throughput.' },
      { name: 'evaluate_capacity_gap',            desc: 'Calculates the shortfall or surplus between forecasted weekly demand and available production capacity for each planning week.' },
      { name: 'optimize_production_mix',          desc: 'Finds the product mix across production lines that maximises gross profit for the planning horizon given demand and capacity constraints.' },
      { name: 'generate_production_requirements', desc: 'Explodes the production plan into a detailed Bill of Materials — exact component quantities needed per week — feeding the Supplier Agent.' },
    ]}
  />
}

// ─── Slide 6e — Supplier Procurement Agent ────────────────────────────────────

function SlideAgentSupplier() {
  return <AgentDetailSlide
    icon={Truck}
    name="Supplier Procurement Agent"
    tagline="Secures the right components from the right suppliers at the right cost"
    color="text-rose-400"
    ring="bg-rose-600/10 border-rose-500/30"
    tagColor="red"
    mission="Evaluates all available suppliers across performance score, delivery reliability, lead time, and supply chain risk. Consumes the component requirements from the Production Agent and generates optimized purchase orders — allocating quantities across multiple suppliers to minimize cost and eliminate single-source risk."
    reads="Component requirements from Production Agent, current component stock levels, open POs in transit, supplier performance history, contract terms, lead times per supplier"
    outputs="Ranked supplier evaluations, optimized purchase order recommendations, supply chain risk score, delivery risk probabilities — all written to the Approval Queue"
    tools={[
      { name: 'get_procurement_context',        desc: 'First tool called. Consolidates component stock levels, in-transit purchase orders, supplier scorecards, contract terms, and incoming material pipeline.' },
      { name: 'evaluate_supplier_options',      desc: 'Ranks all qualified suppliers for a component by cost, lead time, on-time delivery rate, and current availability — with a recommended choice.' },
      { name: 'generate_purchase_orders',       desc: 'Creates purchase orders for all components needed in the planning horizon at economically optimal quantities and supplier splits.' },
      { name: 'assess_supply_chain_risk',       desc: 'Scores overall supply chain risk: single-source dependencies, geographic concentration, financial risk, and contract expiry alerts.' },
      { name: 'simulate_delivery_risk',         desc: 'Calculates the probability of a late delivery from a specific supplier using their full historical performance record.' },
      { name: 'optimize_supplier_allocation',   desc: 'Splits large orders across multiple suppliers to simultaneously minimise total cost and eliminate single-point-of-failure risk.' },
    ]}
  />
}

// ─── Slide 7 — How It Works ───────────────────────────────────────────────────

function SlideHowItWorks() {
  const flow = [
    { label: 'Real Data',       sub: 'Machines · Inventory · Orders', color: '#334155', icon: Database },
    { label: 'Demand Agent',    sub: 'Forecast demand',               color: '#1d4ed8', icon: TrendingUp },
    { label: 'Inventory Agent', sub: 'Check stock & reorder',         color: '#7c3aed', icon: Package },
    { label: 'Machine Agent',   sub: 'Assess health & risk',          color: '#b45309', icon: Cpu },
    { label: 'Production Agent',sub: 'Schedule production',           color: '#065f46', icon: Factory },
    { label: 'Supplier Agent',  sub: 'Evaluate suppliers',            color: '#9f1239', icon: Truck },
    { label: 'Orchestrator',    sub: 'Synthesize master plan',        color: '#4338ca', icon: Brain },
    { label: 'Approval Queue',  sub: 'Manager reviews & approves',    color: '#5b21b6', icon: Shield },
    { label: 'Dashboard Updated',sub:'Audit log recorded',            color: '#1e293b', icon: BarChart3 },
  ]
  const tiers = [
    { freq: 'Every 15 min',   label: 'Machine Health Real-Time Check',        color: 'text-amber-400',  ring: 'bg-amber-600/10 border-amber-500/30' },
    { freq: 'Daily at 6 AM',  label: 'Full 5-Agent Intelligence Pipeline',    color: 'text-indigo-400', ring: 'bg-indigo-600/10 border-indigo-500/30' },
    { freq: 'Weekly Monday',  label: 'Strategic Review + Agent Negotiation',  color: 'text-emerald-400',ring: 'bg-emerald-600/10 border-emerald-500/30' },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel>System Architecture</SectionLabel>
        <SectionTitle>How All Agents Work Together</SectionTitle>

        {/* Flow ribbon */}
        <motion.div variants={fadeUp} className="flex items-center gap-1.5 mb-8 overflow-x-auto pb-2">
          {flow.map(({ label, sub, color, icon: Icon }, i) => (
            <div key={label} className="flex items-center gap-1.5 shrink-0">
              <div className="rounded-xl p-3 text-center min-w-[84px]" style={{ background: color }}>
                <Icon className="h-5 w-5 text-white mx-auto mb-1 opacity-90" />
                <p className="text-white text-[11px] font-semibold leading-tight">{label}</p>
                <p className="text-white/55 text-[9px] leading-tight mt-0.5">{sub}</p>
              </div>
              {i < flow.length - 1 && <ArrowRight className="h-4 w-4 text-slate-600 shrink-0" />}
            </div>
          ))}
        </motion.div>

        {/* Three-tier model */}
        <motion.div variants={fadeUp}>
          <p className="text-xs text-slate-500 font-semibold uppercase tracking-widest mb-3">Three-Tier Execution Model</p>
          <div className="grid grid-cols-3 gap-4">
            {tiers.map(({ freq, label, color, ring }) => (
              <div key={label} className={`px-5 py-4 rounded-xl border ${ring}`}>
                <p className={`text-xl font-black mb-1 ${color}`}>{freq}</p>
                <p className="text-slate-300 text-sm">{label}</p>
              </div>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  )
}

// ─── Slide 8 — Agent Negotiation ─────────────────────────────────────────────

function SlideNegotiation() {
  const steps = [
    { n:'01', title:'Crisis Trigger',       desc:'Manager selects a scenario: Emergency Stockout, Machine Breakdown, Supplier Failure, or Demand Spike.', dot:'bg-red-500' },
    { n:'02', title:'Agents State Position',desc:'Each agent analyzes the crisis from its domain and clearly states its constraints and current status.',   dot:'bg-amber-500' },
    { n:'03', title:'Negotiation Rounds',   desc:'Agents trade off: "If Machine #3 is maintained Thursday, we can safely run 100% for 3 days" + "Emergency order covers the gap."', dot:'bg-indigo-500' },
    { n:'04', title:'Consensus Deal',       desc:'A final agreed plan is formed, showing the cost delta vs. the lost opportunity cost — giving the manager full context.', dot:'bg-emerald-500' },
    { n:'05', title:'One-Click Approval',   desc:'Manager reviews and approves. System auto-creates work order, purchase order, updated schedule, and customer comms draft.', dot:'bg-violet-500' },
  ]
  const voices = [
    { agent:'Demand',     msg:'"Customer needs 2,000 units by Friday — cannot reduce"',               color:'text-blue-300' },
    { agent:'Inventory',  msg:'"Only 1,200 units of parts available. Emergency reorder needed"',       color:'text-purple-300' },
    { agent:'Machine',    msg:'"Machine #3 at 68% failure risk — cannot run at full speed"',          color:'text-amber-300' },
    { agent:'Production', msg:'"Max safe output = 1,400 if Machine #3 is maintained Thursday night"', color:'text-emerald-300' },
    { agent:'Supplier',   msg:'"Best supplier: 500 units delivered in 48 hrs at +15% cost"',          color:'text-rose-300' },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel color="text-violet-400">Agent Negotiation Tab</SectionLabel>
        <SectionTitle>Crisis Resolution in <span className="text-violet-400">60 Seconds</span></SectionTitle>

        <div className="grid gap-8" style={{ gridTemplateColumns: '1fr 1.15fr' }}>
          {/* Steps */}
          <motion.div variants={stagger} className="space-y-3">
            {steps.map(({ n, title, desc, dot }) => (
              <motion.div key={n} variants={fadeUp} className="flex gap-4 items-start">
                <div className={`w-8 h-8 rounded-full ${dot} flex items-center justify-center text-white text-xs font-black shrink-0 mt-0.5`}>
                  {n}
                </div>
                <div>
                  <p className="text-white font-semibold text-sm mb-0.5">{title}</p>
                  <p className="text-slate-400 text-xs leading-relaxed">{desc}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Live example */}
          <motion.div variants={fadeUp}>
            <Glass accent className="h-full p-5">
              <p className="text-indigo-300 font-bold text-sm mb-4 flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Live Example — Tuesday Morning Crisis
              </p>
              <div className="space-y-2.5 mb-4">
                {voices.map(({ agent, msg, color }) => (
                  <div key={agent} className="flex gap-2.5 items-start text-xs">
                    <span className={`font-bold shrink-0 ${color} w-16`}>{agent}:</span>
                    <span className="text-slate-400 italic leading-relaxed">{msg}</span>
                  </div>
                ))}
              </div>
              <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-900/40">
                <p className="text-emerald-300 font-bold text-xs mb-1">Agreed Deal:</p>
                <p className="text-slate-300 text-xs leading-relaxed">
                  Partial shipment (1,400 Fri) + emergency supplier order ($4,200) + 4 hr maintenance Thursday night
                </p>
                <p className="text-emerald-400 font-bold text-xs mt-2">
                  Crisis cost: $4,200 &nbsp;·&nbsp; Lost order value avoided: $38,000
                </p>
              </div>
            </Glass>
          </motion.div>
        </div>
      </motion.div>
    </div>
  )
}

// ─── Slide 9 — Impact & ROI ───────────────────────────────────────────────────

function SlideImpact() {
  const metrics = [
    { to:12000, prefix:'$', suffix:'',     label:'Per prevented machine failure',    sub:'Each Machine Agent decision accepted',      color:'text-amber-400',  ring:'bg-amber-600/10 border-amber-500/30' },
    { to:2500,  prefix:'$', suffix:'',     label:'Per inventory decision accepted',  sub:'Reduced holding costs & emergency orders',  color:'text-blue-400',   ring:'bg-blue-600/10 border-blue-500/30' },
    { to:60,    prefix:'',  suffix:' sec', label:'Crisis resolution time',           sub:'vs. 4+ hours of manual cross-dept meetings', color:'text-indigo-400', ring:'bg-indigo-600/10 border-indigo-500/30' },
    { to:100,   prefix:'',  suffix:'%',    label:'Manager control retained',         sub:'Every AI recommendation requires approval',  color:'text-emerald-400',ring:'bg-emerald-600/10 border-emerald-500/30' },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel color="text-emerald-400">Impact & ROI</SectionLabel>
        <SectionTitle>Real, Measurable Results</SectionTitle>

        <motion.div variants={stagger} className="grid grid-cols-4 gap-4 mb-7">
          {metrics.map(({ to, prefix, suffix, label, sub, color, ring }) => (
            <motion.div key={label} variants={fadeUp}
              whileHover={{ y: -5 }} transition={{ type:'spring', stiffness:280 }}>
              <Glass className={`text-center p-5 h-full ${ring}`}>
                <p className={`text-4xl font-black mb-2 ${color}`}>
                  <Counter to={to} prefix={prefix} suffix={suffix} />
                </p>
                <p className="text-white font-semibold text-sm mb-2">{label}</p>
                <p className="text-slate-500 text-xs">{sub}</p>
              </Glass>
            </motion.div>
          ))}
        </motion.div>

        <motion.div variants={stagger} className="grid grid-cols-2 gap-5">
          <motion.div variants={fadeUp}>
            <Glass className="p-5 border-red-900/25">
              <p className="text-red-400 font-bold mb-3 flex items-center gap-2">
                <XCircle className="h-4 w-4" /> Without AMIS
              </p>
              <ul className="space-y-2 text-sm text-slate-400">
                <li>• Machine fails → <span className="text-red-400">$260K/hr</span> unplanned downtime</li>
                <li>• Emergency supplier order → <span className="text-red-400">40% cost premium</span></li>
                <li>• Stockout → lost customer order worth <span className="text-red-400">$38K</span></li>
                <li>• 4 hours of daily crisis coordination meetings</li>
                <li>• 23% of inventory is either excess or missing</li>
              </ul>
            </Glass>
          </motion.div>
          <motion.div variants={fadeUp}>
            <Glass className="p-5 border-emerald-900/25">
              <p className="text-emerald-400 font-bold mb-3 flex items-center gap-2">
                <CheckCircle className="h-4 w-4" /> With AMIS
              </p>
              <ul className="space-y-2 text-sm text-slate-300">
                <li>• Machine risk flagged 72 hrs early → <span className="text-emerald-400">2-hr planned repair</span></li>
                <li>• Reorder raised before stockout → <span className="text-emerald-400">standard pricing</span></li>
                <li>• Crisis plan negotiated in <span className="text-emerald-400">60 seconds</span>, $34K+ saved</li>
                <li>• One dashboard replaces all daily reporting meetings</li>
                <li>• Live inventory — zero surprise stockouts</li>
              </ul>
            </Glass>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  )
}

// ─── Slide 10 — Future Vision ─────────────────────────────────────────────────

function SlideFuture() {
  const phases = [
    {
      phase:'Phase 1', title:'Multi-Tenant SaaS',
      items:['Isolated data environment per factory','Role-based access: Manager / Executive / Operator','Subscription tiers: Starter → Pro → Enterprise'],
      color:'text-blue-400', ring:'bg-blue-600/10 border-blue-500/30',
    },
    {
      phase:'Phase 2', title:'Canonical Data Model',
      items:['Universal manufacturing data schema','Plug-in adapters: SAP, Oracle, Odoo, CSV','Handles any client data format automatically','"We speak your factory\'s language"'],
      color:'text-indigo-400', ring:'bg-indigo-600/10 border-indigo-500/30',
    },
    {
      phase:'Phase 3', title:'Marketplace & Benchmarking',
      items:['Cross-factory anonymized benchmarks','Agent marketplace: energy, quality, logistics','API access for custom integrations','"Your OEE is 78% — top factories avg 85%"'],
      color:'text-violet-400', ring:'bg-violet-600/10 border-violet-500/30',
    },
  ]
  const market = [
    { value:'$14T',  label:'Global manufacturing industry size',  color:'text-blue-400' },
    { value:'80%',   label:'Still using spreadsheets for planning',color:'text-amber-400' },
    { value:'37%',   label:'YoY AI adoption in manufacturing',     color:'text-emerald-400' },
  ]
  return (
    <div className="flex flex-col h-full justify-center relative">
      <Orbs />
      <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
        <SectionLabel color="text-violet-400">Future Vision</SectionLabel>
        <SectionTitle>Becoming a Global SaaS Platform</SectionTitle>

        <motion.div variants={stagger} className="grid grid-cols-3 gap-5 mb-5">
          {phases.map(({ phase, title, items, color, ring }) => (
            <motion.div key={phase} variants={fadeUp}
              whileHover={{ y:-4 }} transition={{ type:'spring', stiffness:280 }}>
              <Glass className={`h-full p-5 ${ring}`}>
                <p className="text-xs font-bold text-slate-600 mb-1">{phase}</p>
                <p className={`font-bold text-base mb-3 ${color}`}>{title}</p>
                <ul className="space-y-2">
                  {items.map(item => (
                    <li key={item} className="flex items-start gap-2 text-xs text-slate-300">
                      <span className={`${color} font-bold mt-0.5 shrink-0`}>→</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </Glass>
            </motion.div>
          ))}
        </motion.div>

        <motion.div variants={stagger} className="grid grid-cols-3 gap-4 mb-5">
          {market.map(({ value, label, color }) => (
            <motion.div key={label} variants={fadeUp}>
              <Glass className="text-center p-4">
                <p className={`text-3xl font-black mb-1 ${color}`}>{value}</p>
                <p className="text-slate-400 text-xs">{label}</p>
              </Glass>
            </motion.div>
          ))}
        </motion.div>

        <motion.div variants={fadeUp}
          className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/40 to-violet-950/40 border border-indigo-900/30 text-center">
          <p className="text-indigo-200 font-semibold text-base">
            AMIS addresses the #1 pain in manufacturing: the complexity of cross-domain decisions
          </p>
          <p className="text-slate-400 text-sm mt-1">
            One platform · Every factory · Truly intelligent operations
          </p>
        </motion.div>
      </motion.div>
    </div>
  )
}

// ─── Slide registry ────────────────────────────────────────────────────────────

const SLIDES = [
  (props) => <SlideTitle {...props} />,
  () => <SlideProblem />,
  () => <SlideBefore />,
  () => <SlideAfter />,
  () => <SlideWhatIsAMIS />,
  () => <SlideAgents />,
  () => <SlideAgentDemand />,
  () => <SlideAgentInventory />,
  () => <SlideAgentMachine />,
  () => <SlideAgentProduction />,
  () => <SlideAgentSupplier />,
  () => <SlideHowItWorks />,
  () => <SlideNegotiation />,
  () => <SlideImpact />,
  () => <SlideFuture />,
]

// ─── Navigation bar ────────────────────────────────────────────────────────────

function NavBar({ current, total, onPrev, onNext }) {
  return (
    <div className="flex items-center gap-5">
      <button
        onClick={onPrev}
        disabled={current === 0}
        className="p-3 rounded-full bg-white/5 border border-white/10 text-white hover:bg-white/10 disabled:opacity-25 disabled:cursor-not-allowed transition-all hover:scale-105 active:scale-95"
      >
        <ChevronLeft className="h-5 w-5" />
      </button>

      {/* Pill dots */}
      <div className="flex items-center gap-1.5">
        {Array.from({ length: total }).map((_, i) => (
          <div key={i}
            className={`rounded-full transition-all duration-300 ${i === current ? 'w-6 h-2 bg-indigo-400' : 'w-2 h-2 bg-white/20'}`}
          />
        ))}
      </div>

      <button
        onClick={onNext}
        disabled={current === total - 1}
        className="p-3 rounded-full bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-25 disabled:cursor-not-allowed transition-all hover:scale-105 active:scale-95 shadow-lg shadow-indigo-600/25"
      >
        <ChevronRight className="h-5 w-5" />
      </button>
    </div>
  )
}

// ─── Main component ────────────────────────────────────────────────────────────

export default function Presentation() {
  const [current, setCurrent]       = useState(0)
  const [direction, setDirection]   = useState(1)
  const [sidebarOpen, setSidebar]   = useState(false)

  const goTo = useCallback((idx) => {
    if (idx === current || idx < 0 || idx >= SLIDES.length) return
    setDirection(idx > current ? 1 : -1)
    setCurrent(idx)
  }, [current])

  const goNext = useCallback(() => goTo(current + 1), [current, goTo])
  const goPrev = useCallback(() => goTo(current - 1), [current, goTo])

  useEffect(() => {
    const h = (e) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown')  goNext()
      if (e.key === 'ArrowLeft'  || e.key === 'ArrowUp')    goPrev()
      if (e.key === 'Escape')                                setSidebar(false)
    }
    window.addEventListener('keydown', h)
    return () => window.removeEventListener('keydown', h)
  }, [goNext, goPrev])

  const CurrentSlide = SLIDES[current]
  const progress = ((current + 1) / SLIDES.length) * 100

  return (
    <div
      className="fixed inset-0 flex flex-col overflow-hidden select-none"
      style={{ background: 'linear-gradient(135deg, #04091a 0%, #080f22 60%, #060c1e 100%)' }}
    >
      {/* Top progress bar */}
      <div className="h-[3px] bg-white/5 shrink-0">
        <motion.div
          className="h-full"
          style={{ background: 'linear-gradient(90deg, #6366f1, #3b82f6)' }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.45, ease: 'easeOut' }}
        />
      </div>

      {/* Header bar */}
      <div className="flex items-center justify-between px-5 py-3 border-b border-white/[0.05] shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSidebar(v => !v)}
            className="p-2 rounded-lg hover:bg-white/8 transition-colors"
            style={{ background: sidebarOpen ? 'rgba(255,255,255,0.06)' : undefined }}
          >
            {sidebarOpen ? <X className="h-5 w-5 text-slate-400" /> : <Menu className="h-5 w-5 text-slate-400" />}
          </button>
          <div className="flex items-center gap-2">
            <span className="text-xs font-mono text-slate-600">
              {String(current + 1).padStart(2, '0')}&nbsp;/&nbsp;{String(SLIDES.length).padStart(2, '0')}
            </span>
            <span className="text-slate-700">·</span>
            <span className="text-sm font-semibold text-white">{SLIDES_META[current].title}</span>
            <span className="text-xs text-slate-500 hidden sm:inline">{SLIDES_META[current].label}</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span
            className="text-xs font-semibold tracking-widest px-3 py-1.5 rounded-full border"
            style={{ background:'rgba(99,102,241,0.1)', borderColor:'rgba(99,102,241,0.25)', color:'#a5b4fc' }}
          >
            AMIS
          </span>
        </div>
      </div>

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">

        {/* Sidebar */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.nav
              initial={{ x: -272, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -272, opacity: 0 }}
              transition={{ duration: 0.28, ease: 'easeOut' }}
              className="w-64 shrink-0 border-r border-white/[0.05] overflow-y-auto"
              style={{ background: 'rgba(255,255,255,0.015)' }}
            >
              <div className="p-4">
                <p className="text-[10px] font-bold text-slate-600 uppercase tracking-[0.2em] mb-3 px-2">
                  Slides
                </p>
                {SLIDES_META.map(({ title, label }, id) => {
                  const active = id === current
                  return (
                    <button
                      key={id}
                      onClick={() => { goTo(id); setSidebar(false) }}
                      className={`w-full text-left px-3 py-2.5 rounded-xl mb-1 transition-all border ${
                        active
                          ? 'bg-indigo-600/15 border-indigo-500/30'
                          : 'border-transparent hover:bg-white/[0.04]'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <span className={`text-xs font-mono shrink-0 ${active ? 'text-indigo-400' : 'text-slate-700'}`}>
                          {String(id + 1).padStart(2, '0')}
                        </span>
                        <div>
                          <p className={`text-sm font-semibold ${active ? 'text-white' : 'text-slate-400'}`}>{title}</p>
                          <p className="text-xs text-slate-600">{label}</p>
                        </div>
                      </div>
                    </button>
                  )
                })}
              </div>
            </motion.nav>
          )}
        </AnimatePresence>

        {/* Slide canvas */}
        <div className="flex-1 relative overflow-hidden">
          <AnimatePresence custom={direction} mode="wait">
            <motion.div
              key={current}
              custom={direction}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              className="absolute inset-0 px-14 py-8 overflow-y-auto"
            >
              <CurrentSlide onNext={goNext} />
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Footer navigation */}
      <div className="flex items-center justify-center py-4 border-t border-white/[0.05] shrink-0 relative">
        <NavBar current={current} total={SLIDES.length} onPrev={goPrev} onNext={goNext} />
        <span className="absolute right-6 text-xs text-slate-700 hidden md:block">
          ← → arrow keys
        </span>
      </div>
    </div>
  )
}
