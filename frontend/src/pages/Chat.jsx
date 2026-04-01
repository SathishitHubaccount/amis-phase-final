import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Loader2, Sparkles, AlertTriangle, CheckCircle, TrendingUp, Package, Database, Wrench, Cpu } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import Card from '../components/Card'
import { formatDate } from '../lib/utils'

const markdownComponents = {
  h1: ({ children }) => (
    <h1 className="text-xl font-black text-white mt-5 mb-3 first:mt-0 pb-2 border-b border-slate-700">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-base font-bold text-white mt-5 mb-2.5 first:mt-0 flex items-center gap-2">
      <span className="inline-block w-1 h-4 rounded-full bg-primary-500 shrink-0" />
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-sm font-bold text-slate-200 mt-4 mb-2 first:mt-0">{children}</h3>
  ),
  p: ({ children }) => (
    <p className="text-sm text-slate-200 leading-relaxed mb-3 last:mb-0">{children}</p>
  ),
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
    <blockquote className="border-l-4 border-primary-500 pl-4 py-1 my-3 bg-primary-500/5 rounded-r-lg text-slate-300 italic text-sm">
      {children}
    </blockquote>
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
  th: ({ children }) => (
    <th className="px-4 py-2.5 text-left text-xs font-bold text-slate-300 uppercase tracking-wider">{children}</th>
  ),
  td: ({ children }) => (
    <td className="px-4 py-2.5 text-sm text-slate-200 border-t border-slate-700/50">{children}</td>
  ),
}

const TOOL_META = {
  get_inventory_status:     { label: 'Inventory DB',    color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' },
  get_machine_health:       { label: 'Machine DB',      color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
  get_demand_data:          { label: 'Demand DB',       color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  get_production_status:    { label: 'Production DB',   color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  get_supplier_status:      { label: 'Supplier DB',     color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
  get_pipeline_decisions:   { label: 'Audit Log DB',    color: 'text-slate-300 bg-slate-500/10 border-slate-500/20' },
  get_system_health_summary:{ label: 'System Health DB',color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20' },
}

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    }])

    // Add pending AI message
    const pendingId = Date.now()
    setMessages(prev => [...prev, {
      id: pendingId,
      role: 'assistant',
      content: null,
      tools_called: [],
      status: 'pending',
      timestamp: new Date().toISOString(),
    }])
    setLoading(true)

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      })
      const data = await res.json()

      if (!res.ok) throw new Error(data.detail || 'Request failed')

      setMessages(prev => prev.map(m =>
        m.id === pendingId
          ? { ...m, content: data.answer, tools_called: data.tools_called || [], status: 'completed' }
          : m
      ))
    } catch (err) {
      setMessages(prev => prev.map(m =>
        m.id === pendingId
          ? { ...m, content: `Error: ${err.message}`, tools_called: [], status: 'failed' }
          : m
      ))
    } finally {
      setLoading(false)
    }
  }

  const suggestedQuestions = [
    { text: 'Which machines are at critical failure risk right now?', icon: Wrench },
    { text: 'What is our current inventory level and stockout risk?', icon: Package },
    { text: 'Show me recent demand trend for Product A', icon: TrendingUp },
    { text: 'What are our open purchase orders and supplier scores?', icon: CheckCircle },
    { text: 'Give me a full system health summary', icon: Cpu },
    { text: 'Show the last 5 pipeline decisions from the audit log', icon: Database },
  ]

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Ask AMIS</h1>
          <p className="mt-1 text-sm text-slate-400">
            Natural language queries — Claude reads live plant data via MCP
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20">
          <Database className="h-3.5 w-3.5 text-violet-400" />
          <span className="text-xs font-semibold text-violet-400">MCP Connected</span>
        </div>
      </div>

      {/* Chat Container */}
      <Card className="flex-1 flex flex-col overflow-hidden border-slate-700">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="p-5 rounded-2xl bg-gradient-to-br from-violet-500/15 to-primary-500/15 border border-violet-500/20 mb-5">
                <Database className="h-10 w-10 text-violet-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Ask AMIS Anything</h3>
              <p className="text-sm text-slate-400 mb-2 max-w-md leading-relaxed">
                Claude queries your live manufacturing database through MCP tools — real data, every time.
              </p>
              <div className="flex items-center gap-2 mb-8">
                <span className="text-xs text-violet-400 bg-violet-500/10 border border-violet-500/20 px-2 py-0.5 rounded-full font-medium">Inventory</span>
                <span className="text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded-full font-medium">Machines</span>
                <span className="text-xs text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-full font-medium">Demand</span>
                <span className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full font-medium">Production</span>
                <span className="text-xs text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-full font-medium">Suppliers</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
                {suggestedQuestions.map(({ text, icon: Icon }, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(text)}
                    className="flex items-start gap-3 text-left px-4 py-4 text-sm text-slate-300 bg-slate-800/60 hover:bg-slate-700 rounded-xl transition-all border border-slate-700 hover:border-slate-500 group"
                  >
                    <div className="p-1.5 rounded-lg bg-violet-500/10 border border-violet-500/20 shrink-0 group-hover:bg-violet-500/20 transition-colors">
                      <Icon className="h-4 w-4 text-violet-400" />
                    </div>
                    <span className="leading-snug">{text}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <AnimatePresence>
              {messages.map((message, index) => (
                <MessageBubble key={index} message={message} />
              ))}
            </AnimatePresence>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-slate-700 p-4 bg-slate-900/50">
          <form onSubmit={handleSubmit} className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about inventory, machines, demand, production, or suppliers..."
              className="flex-1 px-4 py-3 border border-slate-700 bg-slate-800 text-white placeholder-slate-500 rounded-xl focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-colors text-sm"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="px-5 py-3 bg-gradient-to-r from-violet-600 to-primary-600 text-white rounded-xl font-medium hover:from-violet-500 hover:to-primary-500 disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-violet-500/25"
            >
              {loading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
            </button>
          </form>
        </div>
      </Card>
    </div>
  )
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start`}
    >
      {/* Avatar */}
      <div className={`flex-shrink-0 h-9 w-9 rounded-xl flex items-center justify-center shadow-lg ${
        isUser
          ? 'bg-gradient-to-br from-primary-500 to-accent-500'
          : 'bg-gradient-to-br from-violet-700 to-slate-800 border border-violet-500/30'
      }`}>
        {isUser ? <User className="h-4 w-4 text-white" /> : <Bot className="h-4 w-4 text-violet-300" />}
      </div>

      {/* Content */}
      <div className={`flex flex-col gap-1 ${isUser ? 'items-end max-w-lg' : 'items-start flex-1 min-w-0'}`}>
        {isUser && (
          <div className="px-4 py-3 rounded-2xl rounded-tr-sm bg-gradient-to-r from-primary-600 to-accent-600 shadow-lg shadow-primary-500/20">
            <p className="text-sm text-white font-medium">{message.content}</p>
          </div>
        )}

        {!isUser && (
          <>
            {message.content ? (
              <div className={`w-full rounded-2xl rounded-tl-sm border overflow-hidden shadow-xl ${
                message.status === 'failed'
                  ? 'border-red-500/30 bg-red-500/5'
                  : 'border-slate-700 bg-slate-800/60'
              }`}>
                {/* Header bar */}
                <div className="flex items-center justify-between px-5 py-3 border-b border-slate-700/60 bg-slate-800/80">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-3.5 w-3.5 text-violet-400" />
                    <span className="text-xs font-semibold text-violet-400 uppercase tracking-wide">AMIS · MCP Response</span>
                  </div>
                  {/* MCP tools called badges */}
                  {message.tools_called?.length > 0 && (
                    <div className="flex items-center gap-1.5 flex-wrap justify-end">
                      {[...new Set(message.tools_called)].map((tool) => {
                        const meta = TOOL_META[tool] || { label: tool, color: 'text-slate-400 bg-slate-500/10 border-slate-500/20' }
                        return (
                          <span key={tool} className={`flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full border ${meta.color}`}>
                            <Database className="h-2.5 w-2.5" />
                            {meta.label}
                          </span>
                        )
                      })}
                    </div>
                  )}
                </div>
                {/* Markdown content */}
                <div className="px-6 py-5">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                    {message.content}
                  </ReactMarkdown>
                </div>
              </div>
            ) : message.status === 'pending' ? (
              <div className="flex items-center gap-3 px-5 py-4 rounded-2xl rounded-tl-sm border border-slate-700 bg-slate-800/60">
                <Loader2 className="h-4 w-4 text-violet-400 animate-spin" />
                <span className="text-sm text-slate-400">Querying live database via MCP...</span>
              </div>
            ) : null}
            <span className="text-xs text-slate-600 mt-1 pl-1">{formatDate(message.timestamp)}</span>
          </>
        )}
      </div>
    </motion.div>
  )
}
