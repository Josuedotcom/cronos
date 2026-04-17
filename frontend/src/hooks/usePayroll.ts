import { useCallback, useState } from 'react'
import apiClient from '../api/client'
import { PAYROLL_ENDPOINTS } from '../api/endpoints'
import { usePayrollStore } from '../stores/payrollStore'
import { useAuthStore } from '../stores/authStore'

export function usePayroll() {
  const { setWorkerPayroll, setDailyPayroll, setCompanyPayroll, setError } = usePayrollStore()
  const { user } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)

  const fetchWorkerPayroll = useCallback(
    async (workerId: string, startDate: string, endDate: string) => {
      if (!user) return

      setIsLoading(true)
      try {
        const params = new URLSearchParams({
          start_date: startDate,
          end_date: endDate,
        })
        const url = `${PAYROLL_ENDPOINTS.WORKER(workerId)}?${params.toString()}`
        const response = await apiClient.get(url)
        setWorkerPayroll(response.data)
        setError(null)
        return response.data
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Failed to fetch payroll'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [user, setWorkerPayroll, setError]
  )

  const fetchDailyPayroll = useCallback(
    async (workerId: string, date: string) => {
      if (!user) return

      setIsLoading(true)
      try {
        const params = new URLSearchParams({ date })
        const url = `${PAYROLL_ENDPOINTS.DAILY(workerId)}?${params.toString()}`
        const response = await apiClient.get(url)
        setDailyPayroll(response.data)
        setError(null)
        return response.data
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Failed to fetch daily payroll'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [user, setDailyPayroll, setError]
  )

  const fetchCompanyPayroll = useCallback(
    async (startDate: string, endDate: string) => {
      if (!user) return

      setIsLoading(true)
      try {
        const params = new URLSearchParams({
          start_date: startDate,
          end_date: endDate,
        })
        const url = `${PAYROLL_ENDPOINTS.SUMMARY}?${params.toString()}`
        const response = await apiClient.get(url)
        setCompanyPayroll(response.data)
        setError(null)
        return response.data
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Failed to fetch company payroll'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [user, setCompanyPayroll, setError]
  )

  return {
    isLoading,
    fetchWorkerPayroll,
    fetchDailyPayroll,
    fetchCompanyPayroll,
  }
}
