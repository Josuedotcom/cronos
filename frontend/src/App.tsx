import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import DashboardLayout from './layouts/DashboardLayout'

export default function App() {
  const { isAuthenticated } = useAuthStore()

  return (
    <Router>
      <Routes>
        {isAuthenticated ? (
          <>
            <Route path="/dashboard" element={<DashboardLayout />} />
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
