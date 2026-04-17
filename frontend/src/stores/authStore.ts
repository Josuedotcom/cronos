import { create } from 'zustand'

export interface User {
  id: string
  email: string
  role: 'WORKER' | 'MANAGER' | 'HR_ADMIN'
  company_id: string
  name?: string
}

export interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
  
  setUser: (user: User) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  clearAuth: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  loadFromStorage: () => void
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  loading: false,
  error: null,

  setUser: (user) => set({ user, isAuthenticated: true }),
  
  setTokens: (accessToken, refreshToken) => {
    set({ accessToken, refreshToken })
    localStorage.setItem('accessToken', accessToken)
    localStorage.setItem('refreshToken', refreshToken)
  },
  
  clearAuth: () => {
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      error: null,
    })
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  },
  
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  
  loadFromStorage: () => {
    const accessToken = localStorage.getItem('accessToken')
    const refreshToken = localStorage.getItem('refreshToken')
    
    if (accessToken && refreshToken) {
      set({
        accessToken,
        refreshToken,
        isAuthenticated: true,
      })
    }
  },
  
  login: async (_email: string, _password: string) => {
    set({ loading: true, error: null })
    try {
      // TODO: Implement actual API call to /auth/login
      // For now, this is a placeholder
      throw new Error('Not implemented')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed'
      set({ error: errorMessage, loading: false })
      throw err
    }
  },
  
  logout: () => {
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      error: null,
    })
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  },
}))
