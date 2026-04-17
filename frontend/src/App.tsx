import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import DashboardLayout from './layouts/DashboardLayout'
import ShiftsPage from './pages/ShiftsPage'
import PayrollPage from './pages/PayrollPage'

export default function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Router>
      <Routes>
        {isAuthenticated ? (
          <>
            <Route path="/dashboard" element={<DashboardLayout />}>
              <Route index element={<div className="text-center py-12"><p className="text-gray-500">Bienvenido al Dashboard</p></div>} />
              <Route path="shifts" element={<ShiftsPage />} />
              <Route path="payroll" element={<PayrollPage />} />
            </Route>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </>
        ) : (
          <>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </>
        )}
      </Routes>
    </Router>
  )
}
