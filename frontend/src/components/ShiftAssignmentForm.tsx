import { useState, useEffect } from 'react'
import { useShifts } from '../hooks/useShifts'
import { ShiftAssignment } from '../stores/shiftsStore'
import { X } from 'lucide-react'

interface ShiftAssignmentFormProps {
  assignment?: ShiftAssignment | null
  onSuccess?: () => void
  onCancel?: () => void
}

export default function ShiftAssignmentForm({ assignment, onSuccess, onCancel }: ShiftAssignmentFormProps) {
  const { createAssignment, isLoading } = useShifts()
  const [formData, setFormData] = useState({
    worker_id: '',
    template_id: '',
    date: '',
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    if (assignment) {
      setFormData({
        worker_id: assignment.worker_id,
        template_id: assignment.template_id,
        date: assignment.date,
      })
    }
  }, [assignment])

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.worker_id) {
      newErrors.worker_id = 'Worker is required'
    }
    if (!formData.template_id) {
      newErrors.template_id = 'Template is required'
    }
    if (!formData.date) {
      newErrors.date = 'Date is required'
    } else {
      const selectedDate = new Date(formData.date)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      if (selectedDate < today) {
        newErrors.date = 'Date cannot be in the past'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    try {
      await createAssignment(formData.worker_id, formData.template_id, formData.date)
      setFormData({ worker_id: '', template_id: '', date: '' })
      setErrors({})
      if (onSuccess) {
        onSuccess()
      }
    } catch (err) {
      console.error('Failed to create assignment:', err)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">
            {assignment ? 'Editar Turno' : 'Nuevo Turno'}
          </h2>
          <button
            onClick={onCancel}
            className="p-1 hover:bg-gray-100 rounded text-gray-600 hover:text-gray-900"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Worker ID */}
          <div>
            <label htmlFor="worker_id" className="block text-sm font-medium text-gray-700 mb-1">
              Trabajador
            </label>
            <input
              id="worker_id"
              type="text"
              value={formData.worker_id}
              onChange={(e) => setFormData({ ...formData, worker_id: e.target.value })}
              placeholder="UUID del trabajador"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                errors.worker_id ? 'border-red-500' : 'border-gray-300'
              }`}
              disabled={isLoading}
            />
            {errors.worker_id && (
              <p className="text-red-500 text-sm mt-1">{errors.worker_id}</p>
            )}
          </div>

          {/* Template ID */}
          <div>
            <label htmlFor="template_id" className="block text-sm font-medium text-gray-700 mb-1">
              Plantilla de Turno
            </label>
            <input
              id="template_id"
              type="text"
              value={formData.template_id}
              onChange={(e) => setFormData({ ...formData, template_id: e.target.value })}
              placeholder="UUID de la plantilla"
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                errors.template_id ? 'border-red-500' : 'border-gray-300'
              }`}
              disabled={isLoading}
            />
            {errors.template_id && (
              <p className="text-red-500 text-sm mt-1">{errors.template_id}</p>
            )}
          </div>

          {/* Date */}
          <div>
            <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-1">
              Fecha
            </label>
            <input
              id="date"
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              min={new Date().toISOString().split('T')[0]}
              className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                errors.date ? 'border-red-500' : 'border-gray-300'
              }`}
              disabled={isLoading}
            />
            {errors.date && (
              <p className="text-red-500 text-sm mt-1">{errors.date}</p>
            )}
          </div>

          {/* Buttons */}
          <div className="flex gap-2 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 bg-indigo-600 text-white py-2 rounded-lg font-medium hover:bg-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Guardando...' : 'Guardar'}
            </button>
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 bg-gray-200 text-gray-900 py-2 rounded-lg font-medium hover:bg-gray-300 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
