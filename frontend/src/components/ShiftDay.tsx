import { ShiftAssignment, ShiftTemplate } from '../stores/shiftsStore'
import { Trash2, Clock } from 'lucide-react'

interface ShiftDayProps {
  date: string
  shifts: ShiftAssignment[]
  templates: Map<string, ShiftTemplate>
  onDelete?: (id: string) => void
  onEdit?: (assignment: ShiftAssignment) => void
  readonly?: boolean
}

export default function ShiftDay({ date, shifts, templates, onDelete, onEdit, readonly }: ShiftDayProps) {
  const dayOfWeek = new Date(date).toLocaleDateString('es-ES', { weekday: 'short' })
  const dayNum = new Date(date).getDate()

  // Determine if it's a weekend (for styling)
  const isWeekend = [0, 6].includes(new Date(date).getDay())

  const getShiftColor = (shift: ShiftAssignment) => {
    const template = templates.get(shift.template_id)
    if (!template) return 'bg-gray-200'

    const startHour = parseInt(template.start_time.split(':')[0])
    if (startHour >= 21 || startHour < 6) return 'bg-indigo-200'
    if (startHour >= 6 && startHour < 14) return 'bg-blue-200'
    return 'bg-orange-200'
  }

  return (
    <div className={`p-2 border rounded-lg ${isWeekend ? 'bg-red-50' : 'bg-white'}`}>
      <div className="text-xs font-bold mb-2">
        <span className="text-gray-600">{dayOfWeek.toUpperCase()}</span>
        <span className="ml-2 text-lg text-gray-900">{dayNum}</span>
      </div>

      <div className="space-y-1">
        {shifts.length === 0 ? (
          <p className="text-xs text-gray-400">Sin turno</p>
        ) : (
          shifts.map((shift) => {
            const template = templates.get(shift.template_id)
            return (
              <div key={shift.id} className={`p-2 rounded text-xs ${getShiftColor(shift)}`}>
                <div className="flex items-start justify-between gap-1">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold truncate">{template?.shift_code || 'N/A'}</p>
                    <p className="text-gray-700 flex items-center gap-1">
                      <Clock size={12} />
                      {template?.start_time} - {template?.end_time}
                    </p>
                    {shift.gross_pay && (
                      <p className="text-gray-600 mt-1">
                        ${shift.gross_pay.toFixed(2)}
                      </p>
                    )}
                  </div>
                  {!readonly && (
                    <div className="flex gap-1 flex-shrink-0">
                      {onEdit && (
                        <button
                          onClick={() => onEdit(shift)}
                          className="p-1 hover:bg-white rounded text-gray-600 hover:text-gray-900"
                          title="Edit"
                        >
                          ✏️
                        </button>
                      )}
                      {onDelete && (
                        <button
                          onClick={() => onDelete(shift.id)}
                          className="p-1 hover:bg-white rounded text-red-600 hover:text-red-900"
                          title="Delete"
                        >
                          <Trash2 size={12} />
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
