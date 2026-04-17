import { useState, useEffect } from 'react'
import { usePayroll } from '../hooks/usePayroll'
import { useAuthStore } from '../stores/authStore'
import { DownloadCloud } from 'lucide-react'

export default function PayrollPage() {
  const { user } = useAuthStore()
  const { fetchWorkerPayroll, fetchCompanyPayroll, isLoading } = usePayroll()
  const [startDate, setStartDate] = useState(() => {
    const date = new Date()
    date.setDate(1)
    return date.toISOString().split('T')[0]
  })
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0])
  const [payrollData, setPayrollData] = useState<any>(null)
  const [viewMode, setViewMode] = useState<'personal' | 'company'>('personal')

  useEffect(() => {
    const loadPayroll = async () => {
      try {
        let data
        if (viewMode === 'personal') {
          data = await fetchWorkerPayroll(user?.id || '', startDate, endDate)
        } else {
          data = await fetchCompanyPayroll(startDate, endDate)
        }
        setPayrollData(data)
      } catch (err) {
        console.error('Failed to load payroll:', err)
      }
    }

    if (user?.id) {
      loadPayroll()
    }
  }, [startDate, endDate, viewMode, user?.id, fetchWorkerPayroll, fetchCompanyPayroll])

  const handleExport = (format: 'csv' | 'xml') => {
    if (!payrollData) return

    if (format === 'csv') {
      // Generate CSV
      const headers = ['Date', 'Ordinarias Hours', 'Ordinarias Rate', 'Nocturnas Hours', 'Gross Pay']
      const rows = payrollData.breakdown?.map((row: any) => [
        row.date,
        row.ordinarias_hours,
        row.ordinarias_rate,
        row.nocturnas_hours,
        row.gross_pay,
      ])

      const csv = [headers, ...(rows || [])].map((row) => row.join(',')).join('\n')
      downloadFile(csv, 'payroll.csv', 'text/csv')
    } else if (format === 'xml') {
      // Generate XML
      let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<payroll>\n'
      if (payrollData.breakdown) {
        payrollData.breakdown.forEach((row: any) => {
          xml += `  <entry date="${row.date}" ordinarias_hours="${row.ordinarias_hours}" gross_pay="${row.gross_pay}" />\n`
        })
      }
      xml += '</payroll>'
      downloadFile(xml, 'payroll.xml', 'application/xml')
    }
  }

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    window.URL.revokeObjectURL(url)
  }

  const isManager = user?.role === 'MANAGER' || user?.role === 'HR_ADMIN'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Nómina</h1>
          <p className="text-gray-600 mt-1">Visualiza y exporta tu información de pago</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleExport('csv')}
            disabled={!payrollData}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <DownloadCloud size={18} />
            CSV
          </button>
          <button
            onClick={() => handleExport('xml')}
            disabled={!payrollData}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <DownloadCloud size={18} />
            XML
          </button>
        </div>
      </div>

      {/* View Mode Selector */}
      {isManager && (
        <div className="bg-white rounded-lg shadow-md p-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Modo de Vista</p>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('personal')}
              className={`px-4 py-2 rounded-lg transition ${
                viewMode === 'personal'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
              }`}
            >
              Mi Nómina
            </button>
            <button
              onClick={() => setViewMode('company')}
              className={`px-4 py-2 rounded-lg transition ${
                viewMode === 'company'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
              }`}
            >
              Nómina Empresa
            </button>
          </div>
        </div>
      )}

      {/* Date Filter */}
      <div className="bg-white rounded-lg shadow-md p-4 flex gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Fecha Inicial</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Fecha Final</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      {/* Summary Cards */}
      {payrollData && !isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Total Horas Ordinarias</p>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {payrollData.total_ordinarias_hours?.toFixed(1) || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Total Horas Nocturnas</p>
            <p className="text-3xl font-bold text-indigo-600 mt-2">
              {payrollData.total_nocturnas_hours?.toFixed(1) || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Total Horas Extras</p>
            <p className="text-3xl font-bold text-orange-600 mt-2">
              {payrollData.total_extras_hours?.toFixed(1) || 0}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Pago Total</p>
            <p className="text-3xl font-bold text-green-600 mt-2">
              ${payrollData.total_gross_pay?.toFixed(2) || 0}
            </p>
          </div>
        </div>
      )}

      {/* Payroll Breakdown Table */}
      {payrollData && !isLoading && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Fecha</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Ordinarias (h)
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Nocturnas (h)
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Extras (h)
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Recargos
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                    Pago Bruto
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {payrollData.breakdown?.map((row: any, idx: number) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">{row.date}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{row.ordinarias_hours?.toFixed(2)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{row.nocturnas_hours?.toFixed(2)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{row.extras_hours?.toFixed(2)}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">${row.recargos_amount?.toFixed(2)}</td>
                    <td className="px-6 py-4 text-sm font-semibold text-green-600">
                      ${row.gross_pay?.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {isLoading && (
        <div className="text-center py-12">
          <p className="text-gray-500">Cargando datos de nómina...</p>
        </div>
      )}
    </div>
  )
}
