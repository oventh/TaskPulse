import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Dashboard
export const getDashboardSummary = () => api.get('/dashboard/summary')
export const getDashboardTasks = () => api.get('/dashboard/tasks')

// Agents
export const listAgents = () => api.get('/agents')
export const getAgent = (id) => api.get(`/agents/${id}`)
export const createAgent = (data) => api.post('/agents', data)
export const updateAgent = (id, data) => api.put(`/agents/${id}`, data)

// Tasks
export const listTasks = (agentId) => api.get('/tasks', { params: { agent_id: agentId } })
export const getTask = (id) => api.get(`/tasks/${id}`)
export const createTask = (agentId, data) => api.post('/tasks', data, { params: { agent_id: agentId } })
export const updateTask = (id, data) => api.put(`/tasks/${id}`, data)
export const deleteTask = (id) => api.delete(`/tasks/${id}`)

// Executions
export const listExecutions = (taskId, params) => api.get(`/tasks/${taskId}/executions`, { params })
export const getExecution = (id) => api.get(`/executions/${id}`)
export const getRecentExecutions = (params) => api.get('/executions/recent', { params })

// Alerts
export const listAlerts = (params) => api.get('/alerts', { params })
export const acknowledgeAlert = (id) => api.post(`/alerts/${id}/acknowledge`)

// Notification Channels
export const listChannels = () => api.get('/notification-channels')
export const createChannel = (data) => api.post('/notification-channels', data)
export const updateChannel = (id, data) => api.put(`/notification-channels/${id}`, data)
export const deleteChannel = (id) => api.delete(`/notification-channels/${id}`)

// Alert Rules
export const listAlertRules = (params) => api.get('/alert-rules', { params })
export const createAlertRule = (data) => api.post('/alert-rules', data)
export const deleteAlertRule = (id) => api.delete(`/alert-rules/${id}`)

// System Config
export const getSystemConfig = () => api.get('/system/config')
export const saveSystemConfig = (data) => api.put('/system/config', data)

export default api
