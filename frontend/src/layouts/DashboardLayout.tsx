import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Menu, X, LogOut, User } from 'lucide-react'

export default function DashboardLayout() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const menuItems = [
    { label: 'Dashboard', href: '/dashboard', icon: '📊' },
    { label: 'Shifts', href: '/dashboard/shifts', icon: '📅' },
    { label: 'Payroll', href: '/dashboard/payroll', icon: '💰' },
    ...(user?.role === 'MANAGER' || user?.role === 'HR_ADMIN'
      ? [
          { label: 'Swap Requests', href: '/dashboard/swaps', icon: '🔄' },
          { label: 'Admin', href: '/dashboard/admin', icon: '⚙️' },
        ]
      : []),
  ]

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gray-900 text-white transition-all duration-300 flex flex-col`}
      >
        <div className="p-4 flex items-center justify-between">
          {sidebarOpen && <h2 className="text-xl font-bold">Cronos</h2>}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-gray-800 rounded"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className="flex-1 px-2 py-4 space-y-2">
          {menuItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="flex items-center px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors"
            >
              <span className="text-xl">{item.icon}</span>
              {sidebarOpen && <span className="ml-3">{item.label}</span>}
            </a>
          ))}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <button
            onClick={() => setUserMenuOpen(!userMenuOpen)}
            className="w-full flex items-center px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors relative"
          >
            <User size={20} />
            {sidebarOpen && <span className="ml-3 truncate">{user?.email}</span>}
            
            {userMenuOpen && (
              <div className="absolute left-0 bottom-full mb-2 w-full bg-gray-800 rounded-lg shadow-lg z-50">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center px-4 py-2 text-red-400 hover:bg-gray-700 rounded-lg"
                >
                  <LogOut size={16} />
                  <span className="ml-2">Logout</span>
                </button>
              </div>
            )}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900">{user?.name || user?.email}</p>
            <p className="text-xs text-gray-600 capitalize">{user?.role}</p>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto p-6">
          <div className="bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Welcome to Cronos</h2>
            <p className="text-gray-600">
              This is your dashboard. Navigate using the sidebar to view shifts, payroll, and manage your schedule.
            </p>
          </div>
        </main>
      </div>
    </div>
  )
}
