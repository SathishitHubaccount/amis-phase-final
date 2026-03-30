import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  headers: {
    'Content-Type': 'application/json',
  },
})

// API functions
export const apiClient = {
  // Health check
  health: () => api.get('/api/health'),

  // Dashboard
  getDashboardSummary: () => api.get('/api/dashboard/summary'),

  // Agent runs
  runAgent: (agentType, prompt, productId = 'PROD-A') =>
    api.post('/api/agents/run', { agent_type: agentType, prompt, product_id: productId }),

  getAgentRun: (runId) => api.get(`/api/agents/runs/${runId}`),

  // Pipeline runs
  runPipeline: (productId = 'PROD-A') =>
    api.post('/api/pipeline/run', { product_id: productId }),

  getPipelineRun: (runId) => api.get(`/api/pipeline/runs/${runId}`),

  listPipelineRuns: (limit = 10) =>
    api.get('/api/pipeline/runs', { params: { limit } }),

  // Chat
  chat: (message, sessionId = null) =>
    api.post('/api/chat', { message, session_id: sessionId }),

  // Products
  getProducts: () => api.get('/api/products'),
  getProduct: (productId) => api.get(`/api/products/${productId}`),
  getProductInventory: (productId) => api.get(`/api/products/${productId}/inventory`),
  getProductBOM: (productId) => api.get(`/api/products/${productId}/bom`),

  // Machines
  getMachines: (productId = null) =>
    api.get('/api/machines', { params: productId ? { product_id: productId } : {} }),
  getMachineDetail: (machineId) => api.get(`/api/machines/${machineId}`),

  // Work Orders
  createWorkOrder: (workOrder) => api.post('/api/work-orders', workOrder),
  getWorkOrders: (machineId = null, limit = 50) =>
    api.get('/api/work-orders', { params: { machine_id: machineId, limit } }),
  updateWorkOrderStatus: (woId, status) =>
    api.patch(`/api/work-orders/${woId}/status`, { status }),

  // Suppliers
  getSuppliers: () => api.get('/api/suppliers'),
  getSupplierDetail: (supplierId) => api.get(`/api/suppliers/${supplierId}`),
  getPurchaseOrders: (status = null) => api.get('/api/purchase-orders', { params: status ? { status } : {} }),

  // Activity Log
  getActivityLog: (limit = 100) => api.get('/api/activity-log', { params: { limit } }),

  // Database Stats
  getDatabaseStats: () => api.get('/api/database/stats'),

  // Production Planning
  getProductionLines: (productId = null) =>
    api.get('/api/production/lines', { params: productId ? { product_id: productId } : {} }),
  getProductionSchedule: (productId, weeks = 4) =>
    api.get(`/api/production/schedule/${productId}`, { params: { weeks } }),

  // History/Trends for Charts
  getInventoryHistory: (productId, days = 30) =>
    api.get(`/api/inventory/${productId}/history`, { params: { days } }),
  getMachineOEEHistory: (machineId, days = 30) =>
    api.get(`/api/machines/${machineId}/oee-history`, { params: { days } }),

  // Inventory Adjustment
  adjustInventory: (productId, quantity, reason, user = 'User') =>
    api.post(`/api/inventory/${productId}/adjust`, { quantity, reason, user }),

  // Demand Forecasting
  createDemandForecast: (productId, weekNumber, forecastData) =>
    api.post('/api/demand/forecast', { product_id: productId, week_number: weekNumber, ...forecastData }),
  getDemandForecasts: (productId, weeks = 12) =>
    api.get(`/api/demand/forecast/${productId}`, { params: { weeks } }),
  updateActualDemand: (productId, week, actual) =>
    api.patch(`/api/demand/actual/${productId}/${week}`, { actual }),

  // Production Schedule
  updateProductionSchedule: (scheduleId, updates) =>
    api.put(`/api/production/schedule/${scheduleId}`, updates),

  // AI Forecast Integration
  getLatestAIForecast: (productId) =>
    api.get(`/api/pipeline/latest-forecast/${productId}`),

  // Decisions (Audit Log)
  saveDecision: (agentType, title, status, actionBy = 'Manager', note = null, detail = null) =>
    api.post('/api/decisions', { agent_type: agentType, title, status, action_by: actionBy, note, detail }),
  getDecisions: (limit = 50) => api.get('/api/decisions', { params: { limit } }),

  // Approval system
  getPendingApprovals: () => api.get('/api/approvals/pending'),
  decideApproval: (decisionId, action, approvedBy = 'Manager', notes = null) =>
    api.post(`/api/approvals/${decisionId}/decide`, { action, approved_by: approvedBy, notes }),
}

export default api
