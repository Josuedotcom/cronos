import { useCallback, useState } from 'react'
import apiClient from '../api/client'
import { SHIFT_ENDPOINTS } from '../api/endpoints'
import { useShiftsStore } from '../stores/shiftsStore'
import { useAuthStore } from '../stores/authStore'

export function useShifts() {
  const { templates, assignments, setTemplates, setAssignments, setError, setLoading } = useShiftsStore()
  const { user } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)

  const fetchTemplates = useCallback(async () => {
    if (!user) return
    
    setIsLoading(true)
    setLoading(true)
    try {
      const response = await apiClient.get(SHIFT_ENDPOINTS.TEMPLATES)
      setTemplates(response.data)
      setError(null)
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to fetch templates'
      setError(errorMsg)
    } finally {
      setIsLoading(false)
      setLoading(false)
    }
  }, [user, setTemplates, setError, setLoading])

  const fetchAssignments = useCallback(
    async (startDate: string, endDate: string, workerId?: string) => {
      if (!user) return

      setIsLoading(true)
      setLoading(true)
      try {
        const params = new URLSearchParams({
          start_date: startDate,
          end_date: endDate,
        })
        if (workerId) {
          params.append('worker_id', workerId)
        }

        const response = await apiClient.get(`${SHIFT_ENDPOINTS.ASSIGNMENTS}?${params.toString()}`)
        setAssignments(response.data)
        setError(null)
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Failed to fetch assignments'
        setError(errorMsg)
      } finally {
        setIsLoading(false)
        setLoading(false)
      }
    },
    [user, setAssignments, setError, setLoading]
  )

  const createAssignment = useCallback(
    async (workerId: string, templateId: string, date: string) => {
      setIsLoading(true)
      try {
        const response = await apiClient.post(SHIFT_ENDPOINTS.ASSIGNMENTS, {
          worker_id: workerId,
          template_id: templateId,
          date,
        })
        setError(null)
        return response.data
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Failed to create assignment'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [setError]
  )

  const deleteAssignment = useCallback(
    async (id: string) => {
      setIsLoading(true)
      try {
        await apiClient.delete(SHIFT_ENDPOINTS.ASSIGNMENT(id))
        setError(null)
      } catch (err: any) {
        const errorMsg = err.response?.data?.detail || 'Failed to delete assignment'
        setError(errorMsg)
        throw err
      } finally {
        setIsLoading(false)
      }
    },
    [setError]
  )

  return {
    templates,
    assignments,
    isLoading,
    fetchTemplates,
    fetchAssignments,
    createAssignment,
    deleteAssignment,
  }
}
