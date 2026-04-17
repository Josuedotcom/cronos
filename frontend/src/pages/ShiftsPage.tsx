import { useState } from 'react'
import ShiftCalendar from '../components/ShiftCalendar'
import ShiftAssignmentForm from '../components/ShiftAssignmentForm'
import { ShiftAssignment } from '../stores/shiftsStore'
import { useAuthStore } from '../stores/authStore'

export default function ShiftsPage() {
  const { user } = useAuthStore()
  const [selectedShift, setSelectedShift] = useState<ShiftAssignment | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingAssignment, setEditingAssignment] = useState<ShiftAssignment | null>(null)

  const isManager = user?.role === 'MANAGER' || user?.role === 'HR_ADMIN'

  const handleSelectShift = (shift: ShiftAssignment) => {
    setSelectedShift(shift)
  }

  const handleCreateNew = () => {
    setEditingAssignment(null)
    setShowForm(true)
  }

  const handleEdit = (shift: ShiftAssignment) => {
    setEditingAssignment(shift)
    setShowForm(true)
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingAssignment(null)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Turnos</h1>
          <p className="text-gray-600 mt-1">Visualiza y gestiona los turnos de trabajo</p>
        </div>
        {isManager && (
          <button
            onClick={handleCreateNew}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-medium"
          >
            + Nuevo Turno
          </button>
        )}
      </div>

      {showForm && (
        <ShiftAssignmentForm
          assignment={editingAssignment}
          onSuccess={() => {
            handleCloseForm()
            // Refresh calendar will be handled by store updates
          }}
          onCancel={handleCloseForm}
        />
      )}

      <ShiftCalendar
        workerId={!isManager ? user?.id : undefined}
        readonly={!isManager}
        onSelectShift={handleSelectShift}
      />

      {selectedShift && isManager && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Detalles del Turno</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Fecha</p>
              <p className="text-lg font-semibold text-gray-900">{selectedShift.date}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Trabajador ID</p>
              <p className="text-lg font-semibold text-gray-900">{selectedShift.worker_id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Plantilla</p>
              <p className="text-lg font-semibold text-gray-900">{selectedShift.template_id}</p>
            </div>
            {selectedShift.gross_pay && (
              <div>
                <p className="text-sm text-gray-600">Pago Bruto</p>
                <p className="text-lg font-semibold text-green-600">${selectedShift.gross_pay.toFixed(2)}</p>
              </div>
            )}
          </div>
          <div className="mt-6 flex gap-2">
            <button
              onClick={() => handleEdit(selectedShift)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Editar
            </button>
            <button
              onClick={() => setSelectedShift(null)}
              className="px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 transition"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
