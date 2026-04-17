// Auth endpoints
export const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  REFRESH: '/auth/refresh',
  LOGOUT: '/auth/logout',
}

// Shift endpoints
export const SHIFT_ENDPOINTS = {
  TEMPLATES: '/shifts/templates',
  TEMPLATE: (id: string) => `/shifts/templates/${id}`,
  ASSIGNMENTS: '/shifts/assignments',
  ASSIGNMENT: (id: string) => `/shifts/assignments/${id}`,
}

// Holiday endpoints
export const HOLIDAY_ENDPOINTS = {
  LIST: '/holidays',
  CREATE: '/holidays',
  DELETE: (id: string) => `/holidays/${id}`,
}

// Payroll endpoints
export const PAYROLL_ENDPOINTS = {
  WORKER: (workerId: string) => `/payroll/worker/${workerId}`,
  DAILY: (workerId: string) => `/payroll/daily/${workerId}`,
  SUMMARY: '/payroll/summary',
}
