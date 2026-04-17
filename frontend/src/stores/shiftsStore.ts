import { create } from 'zustand'

export interface ShiftTemplate {
  id: string
  name: string
  start_time: string // HH:MM
  end_time: string   // HH:MM
  shift_code: string
  company_id: string
}

export interface ShiftAssignment {
  id: string
  worker_id: string
  template_id: string
  date: string // YYYY-MM-DD
  gross_pay?: number
  ordinarias_hours?: number
  nocturnas_hours?: number
  extras_hours?: number
  recargos?: number
}

export interface ShiftsState {
  templates: ShiftTemplate[]
  assignments: ShiftAssignment[]
  loading: boolean
  error: string | null
  
  setTemplates: (templates: ShiftTemplate[]) => void
  setAssignments: (assignments: ShiftAssignment[]) => void
  addAssignment: (assignment: ShiftAssignment) => void
  removeAssignment: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  fetchTemplates: () => Promise<void>
  fetchAssignments: (startDate: string, endDate: string, workerId?: string) => Promise<void>
}

export const useShiftsStore = create<ShiftsState>((set, get) => ({
  templates: [],
  assignments: [],
  loading: false,
  error: null,

  setTemplates: (templates) => set({ templates }),
  setAssignments: (assignments) => set({ assignments }),
  
  addAssignment: (assignment) => {
    const current = get().assignments
    set({ assignments: [...current, assignment] })
  },
  
  removeAssignment: (id) => {
    const filtered = get().assignments.filter((a) => a.id !== id)
    set({ assignments: filtered })
  },
  
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  fetchTemplates: async () => {
    set({ loading: true, error: null })
    try {
      // TODO: Implement API call to GET /shifts/templates
      throw new Error('Not implemented')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch templates'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },
  
  fetchAssignments: async (_startDate: string, _endDate: string, _workerId?: string) => {
    set({ loading: true, error: null })
    try {
      // TODO: Implement API call to GET /shifts/assignments?start_date=...&end_date=...
      throw new Error('Not implemented')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch assignments'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },
}))
