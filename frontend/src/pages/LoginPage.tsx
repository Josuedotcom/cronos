import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import apiClient from '../api/client'
import { AUTH_ENDPOINTS } from '../api/endpoints'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setUser, setTokens, setLoading, setError, loading, error } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [validationError, setValidationError] = useState<Record<string, string>>({})

  const validateForm = () => {
    const errors: Record<string, string> = {}
    
    if (!email) {
      errors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Invalid email format'
    }
    
    if (!password) {
      errors.password = 'Password is required'
    } else if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters'
    }
    
    setValidationError(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.post(AUTH_ENDPOINTS.LOGIN, {
        email,
        password,
      })

      const { access_token, refresh_token, user } = response.data
      
      setTokens(access_token, refresh_token)
      setUser(user)
      navigate('/dashboard')
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Login failed'
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="w-full max-w-md bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Cronos</h1>
          <p className="text-gray-600 mt-2">Gestión de Turnos Laboral</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email Input */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                validationError.email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="user@example.com"
              disabled={loading}
            />
            {validationError.email && (
              <p className="text-red-500 text-sm mt-1">{validationError.email}</p>
            )}
          </div>

          {/* Password Input */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                validationError.password ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="••••••••"
              disabled={loading}
            />
            {validationError.password && (
              <p className="text-red-500 text-sm mt-1">{validationError.password}</p>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-6"
          >
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>

        <p className="text-center text-gray-600 text-sm mt-6">
          Demo credentials: Use any email with password of at least 8 characters
        </p>
      </div>
    </div>
  )
}
