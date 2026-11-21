import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Employees
export const employeeAPI = {
  list: (page = 0, limit = 10) =>
    api.get('/api/employees', { params: { skip: page * limit, limit } }),
  get: (id: string) => api.get(`/api/employees/${id}`),
  create: (data: any) => api.post('/api/employees', data),
  update: (id: string, data: any) => api.put(`/api/employees/${id}`, data),
}

// Brands
export const brandAPI = {
  list: (page = 0, limit = 10) =>
    api.get('/api/brands', { params: { skip: page * limit, limit } }),
  get: (id: string) => api.get(`/api/brands/${id}`),
  create: (data: any) => api.post('/api/brands', data),
}

// Processes
export const processAPI = {
  list: () => api.get('/api/processes', { params: { skip: 0, limit: 100 } }),
  create: (data: any) => api.post('/api/processes', data),
}

// Pods
export const podAPI = {
  list: (page = 0, limit = 10) =>
    api.get('/api/pods', { params: { skip: page * limit, limit } }),
  get: (id: string) => api.get(`/api/pods/${id}`),
  create: (data: any) => api.post('/api/pods', data),
}

// Scheduling
export const schedulingAPI = {
  generate: (rosterName: string, month: number, year: number) =>
    api.post('/api/scheduling/generate', { roster_name: rosterName, month, year }),
  validate: (rosterId: string) =>
    api.post('/api/scheduling/validate', { roster_id: rosterId }),
}

// Rosters
export const rosterAPI = {
  list: (page = 0, limit = 10) =>
    api.get('/api/rosters', { params: { skip: page * limit, limit } }),
  get: (id: string) => api.get(`/api/rosters/${id}`),
  publish: (id: string) => api.post(`/api/rosters/${id}/publish`),
  archive: (id: string) => api.post(`/api/rosters/${id}/archive`),
  coverage: (id: string) => api.get(`/api/rosters/${id}/coverage`),
  entries: (id: string, page = 0, limit = 100) =>
    api.get(`/api/rosters/${id}/entries`, { params: { skip: page * limit, limit } }),
}

// Conflicts
export const conflictAPI = {
  list: (rosterId: string, page = 0, limit = 10) =>
    api.get('/api/conflicts', {
      params: { roster_id: rosterId, skip: page * limit, limit },
    }),
  summary: (rosterId: string) =>
    api.get(`/api/conflicts/roster/${rosterId}/summary`),
  resolve: (id: string) => api.post(`/api/conflicts/${id}/resolve`),
}

// Health
export const healthAPI = {
  check: () => api.get('/health'),
}

export default api
