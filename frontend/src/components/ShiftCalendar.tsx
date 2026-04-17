import { useState, useEffect, useMemo } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useShifts } from '../hooks/useShifts'
import { useAuthStore } from '../stores/authStore'
import ShiftDay from '../components/ShiftDay'
import { ShiftAssignment, ShiftTemplate } from '../stores/shiftsStore'

interface ShiftCalendarProps {
  workerId?: string // If provided, show only this worker's shifts
  readonly?: boolean
  onSelectShift?: (shift: ShiftAssignment) => void
}

export default function ShiftCalendar({ workerId, readonly = false, onSelectShift }: ShiftCalendarProps) {
  const { user } = useAuthStore()
  const { templates, assignments, fetchTemplates, fetchAssignments, isLoading } = useShifts()
  const [currentDate, setCurrentDate] = useState(new Date())
  const [viewMode, setViewMode] = useState<'week' | 'month'>('month')

  // Fetch data on mount
  useEffect(() => {
    fetchTemplates()
  }, [fetchTemplates])

  // Fetch assignments when date or workerId changes
  useEffect(() => {
    const startDate = new Date(currentDate)
    const endDate = new Date(currentDate)

    if (viewMode === 'week') {
      startDate.setDate(currentDate.getDate() - currentDate.getDay())
      endDate.setDate(startDate.getDate() + 6)
    } else {
      startDate.setDate(1)
      endDate.setDate(0) // Last day of previous month... wait, this is wrong
      endDate.setMonth(endDate.getMonth() + 1)
      endDate.setDate(0)
    }

    fetchAssignments(
      startDate.toISOString().split('T')[0],
      endDate.toISOString().split('T')[0],
      workerId || user?.id
    )
  }, [currentDate, viewMode, workerId, user?.id, fetchAssignments])

  // Create a map of templates for quick lookup
  const templatesMap = useMemo(() => {
    const map = new Map<string, ShiftTemplate>()
    templates.forEach((t) => map.set(t.id, t))
    return map
  }, [templates])

  // Group assignments by date
  const assignmentsByDate = useMemo(() => {
    const map = new Map<string, ShiftAssignment[]>()
    assignments.forEach((a) => {
      if (!map.has(a.date)) {
        map.set(a.date, [])
      }
      map.get(a.date)!.push(a)
    })
    return map
  }, [assignments])

  // Generate calendar days
  const calendarDays = useMemo(() => {
    const days: (Date | null)[] = []
    const year = currentDate.getFullYear()
    const month = currentDate.getMonth()

    // Get first day of month
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)

    // Add padding days from previous month
    const startDayOfWeek = firstDay.getDay()
    for (let i = startDayOfWeek - 1; i >= 0; i--) {
      days.push(new Date(year, month, -i))
    }

    // Add days of current month
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push(new Date(year, month, i))
    }

    // Add padding days for next month
    const remainingDays = 42 - days.length // 6 weeks * 7 days
    for (let i = 1; i <= remainingDays; i++) {
      days.push(new Date(year, month + 1, i))
    }

    return days
  }, [currentDate])

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))
  }

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))
  }

  const handleToday = () => {
    setCurrentDate(new Date())
  }

  const handleDelete = (assignmentId: string) => {
    if (confirm('¿Estás seguro de que deseas eliminar este turno?')) {
      // TODO: Implement delete API call
      console.log('Delete assignment:', assignmentId)
    }
  }

  const monthName = currentDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' })

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 capitalize">{monthName}</h2>
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => setViewMode('week')}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === 'week' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              Semana
            </button>
            <button
              onClick={() => setViewMode('month')}
              className={`px-3 py-1 rounded text-sm ${
                viewMode === 'month' ? 'bg-indigo-600 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              Mes
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handlePrevMonth}
            className="p-2 hover:bg-gray-200 rounded-lg transition"
          >
            <ChevronLeft size={20} />
          </button>
          <button
            onClick={handleToday}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition text-sm font-medium"
          >
            Hoy
          </button>
          <button
            onClick={handleNextMonth}
            className="p-2 hover:bg-gray-200 rounded-lg transition"
          >
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500">Cargando turnos...</p>
        </div>
      )}

      {!isLoading && (
        <>
          {/* Weekday headers */}
          <div className="grid grid-cols-7 gap-2 mb-2">
            {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sab'].map((day) => (
              <div key={day} className="text-center font-bold text-gray-600 py-2">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar grid */}
          <div className="grid grid-cols-7 gap-2">
            {calendarDays.map((day, idx) => {
              if (!day) return <div key={idx} className="aspect-square" />

              const dateStr = day.toISOString().split('T')[0]
              const dayShifts = assignmentsByDate.get(dateStr) || []
              const isCurrentMonth = day.getMonth() === currentDate.getMonth()

              return (
                <div
                  key={idx}
                  className={`aspect-square ${!isCurrentMonth ? 'opacity-50' : ''}`}
                  onClick={() => dayShifts.length > 0 && onSelectShift && dayShifts[0] && onSelectShift(dayShifts[0])}
                >
                  <ShiftDay
                    date={dateStr}
                    shifts={dayShifts}
                    templates={templatesMap}
                    onDelete={!readonly ? handleDelete : undefined}
                    readonly={readonly}
                  />
                </div>
              )
            })}
          </div>
        </>
      )}

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-200 flex gap-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-200 rounded"></div>
          <span>Turno Día (6am-2pm)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-orange-200 rounded"></div>
          <span>Turno Tarde (2pm-10pm)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-indigo-200 rounded"></div>
          <span>Turno Noche (10pm-6am)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-100 rounded"></div>
          <span>Fin de semana</span>
        </div>
      </div>
    </div>
  )
}
