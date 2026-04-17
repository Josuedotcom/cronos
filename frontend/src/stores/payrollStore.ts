import { create } from 'zustand'

export interface PayrollBreakdown {
  date: string // YYYY-MM-DD
  ordinarias_hours: number
  ordinarias_rate: number
  nocturnas_hours: number
  nocturnas_rate: number
  extras_hours: number
  extras_rate: number
  recargos_amount: number
  gross_pay: number
}

export interface PayrollSummary {
  period_start: string
  period_end: string
  total_ordinarias_hours: number
  total_nocturnas_hours: number
  total_extras_hours: number
  total_recargos: number
  total_gross_pay: number
  breakdown: PayrollBreakdown[]
}

export interface PayrollState {
  workerPayroll: PayrollSummary | null
  dailyPayroll: PayrollBreakdown | null
  companyPayroll: PayrollSummary | null
  loading: boolean
  error: string | null
  
  setWorkerPayroll: (payroll: PayrollSummary | null) => void
  setDailyPayroll: (payroll: PayrollBreakdown | null) => void
  setCompanyPayroll: (payroll: PayrollSummary | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  fetchWorkerPayroll: (workerId: string, startDate: string, endDate: string) => Promise<void>
  fetchDailyPayroll: (workerId: string, date: string) => Promise<void>
  fetchCompanyPayroll: (startDate: string, endDate: string) => Promise<void>
}

export const usePayrollStore = create<PayrollState>((set) => ({
  workerPayroll: null,
  dailyPayroll: null,
  companyPayroll: null,
  loading: false,
  error: null,

  setWorkerPayroll: (payroll) => set({ workerPayroll: payroll }),
  setDailyPayroll: (payroll) => set({ dailyPayroll: payroll }),
  setCompanyPayroll: (payroll) => set({ companyPayroll: payroll }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),

  fetchWorkerPayroll: async (_workerId: string, _startDate: string, _endDate: string) => {
    set({ loading: true, error: null })
    try {
      // TODO: Implement API call to GET /payroll/worker/{worker_id}?start_date=...&end_date=...
      throw new Error('Not implemented')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch payroll'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },

  fetchDailyPayroll: async (_workerId: string, _date: string) => {
    set({ loading: true, error: null })
    try {
      // TODO: Implement API call to GET /payroll/daily/{worker_id}?date=...
      throw new Error('Not implemented')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch daily payroll'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },

  fetchCompanyPayroll: async (_startDate: string, _endDate: string) => {
    set({ loading: true, error: null })
    try {
      // TODO: Implement API call to GET /payroll/summary?start_date=...&end_date=...
      throw new Error('Not implemented')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch company payroll'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },
}))
