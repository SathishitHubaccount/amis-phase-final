import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react'
import Card, { CardHeader, CardTitle, CardContent } from '../components/Card'
import Badge from '../components/Badge'
import { apiClient } from '../lib/api'
import { formatDate } from '../lib/utils'

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = useMutation({
    mutationFn: (message) => apiClient.chat(message, sessionId),
    onSuccess: (data) => {
      const runId = data.data.run_id
      const agentRouted = data.data.agent_routed

      // Add assistant pending message
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: null,
          runId,
          agentRouted,
          status: 'pending',
          timestamp: new Date().toISOString(),
        },
      ])

      // Poll for result
      pollForResult(runId)
    },
  })

  const pollForResult = async (runId) => {
    const maxAttempts = 60 // 2 minutes max
    let attempts = 0

    const poll = async () => {
      try {
        const response = await apiClient.getAgentRun(runId)
        const run = response.data

        if (run.status === 'completed') {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.runId === runId
                ? { ...msg, content: run.result, status: 'completed' }
                : msg
            )
          )
        } else if (run.status === 'failed') {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.runId === runId
                ? {
                    ...msg,
                    content: `Error: ${run.error}`,
                    status: 'failed',
                  }
                : msg
            )
          )
        } else if (attempts < maxAttempts) {
          attempts++
          setTimeout(poll, 2000)
        } else {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.runId === runId
                ? {
                    ...msg,
                    content: 'Request timed out. Please try again.',
                    status: 'failed',
                  }
                : msg
            )
          )
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }

    poll()
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim()) return

    // Add user message
    setMessages((prev) => [
      ...prev,
      {
        role: 'user',
        content: input,
        timestamp: new Date().toISOString(),
      },
    ])

    // Send to API
    sendMessage.mutate(input)
    setInput('')
  }

  const suggestedQuestions = [
    'Why is production attainment lower this week?',
    'What is the stockout risk for Product A?',
    'When should I schedule maintenance for Machine 2?',
    'What are the top supply chain risks right now?',
  ]

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Ask AMIS</h1>
        <p className="mt-1 text-sm text-gray-500">
          Natural language queries powered by AI agents
        </p>
      </div>

      {/* Chat Container */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <div className="p-4 rounded-full bg-gradient-to-br from-primary-50 to-accent-50 mb-4">
                <Sparkles className="h-8 w-8 text-primary-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Ask AMIS Anything
              </h3>
              <p className="text-sm text-gray-500 mb-6 max-w-md">
                I can help you understand demand trends, inventory risks, machine health,
                production planning, and supplier performance.
              </p>
              <div className="space-y-2 w-full max-w-md">
                <p className="text-xs font-medium text-gray-700 mb-2">
                  Try asking:
                </p>
                {suggestedQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => setInput(question)}
                    className="w-full text-left px-4 py-3 text-sm text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200"
                  >
                    {question}
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
        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about demand, inventory, machines, production, or suppliers..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              disabled={sendMessage.isPending}
            />
            <button
              type="submit"
              disabled={!input.trim() || sendMessage.isPending}
              className="px-6 py-3 bg-gradient-to-r from-primary-600 to-accent-600 text-white rounded-lg font-medium hover:from-primary-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all shadow-lg shadow-primary-500/30"
            >
              {sendMessage.isPending ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
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
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
          isUser
            ? 'bg-gradient-to-br from-primary-500 to-accent-500'
            : 'bg-gray-100'
        }`}
      >
        {isUser ? (
          <User className="h-5 w-5 text-white" />
        ) : (
          <Bot className="h-5 w-5 text-gray-600" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={`flex-1 max-w-3xl ${
          isUser ? 'flex flex-col items-end' : 'flex flex-col items-start'
        }`}
      >
        <div
          className={`px-4 py-3 rounded-lg ${
            isUser
              ? 'bg-gradient-to-r from-primary-600 to-accent-600 text-white'
              : 'bg-gray-100 text-gray-900'
          }`}
        >
          {message.content ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : message.status === 'pending' ? (
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Thinking...</span>
              {message.agentRouted && (
                <Badge variant="info" className="ml-2">
                  {message.agentRouted}
                </Badge>
              )}
            </div>
          ) : null}
        </div>
        <p className="text-xs text-gray-500 mt-1 px-1">
          {formatDate(message.timestamp)}
        </p>
      </div>
    </motion.div>
  )
}
