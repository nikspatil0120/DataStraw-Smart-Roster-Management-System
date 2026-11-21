import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  Building2,
  Boxes,
  Users2,
  Calendar,
  AlertTriangle,
  BarChart3,
} from 'lucide-react'

const menuItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/employees', label: 'Employees', icon: Users },
  { path: '/brands', label: 'Brands', icon: Building2 },
  { path: '/processes', label: 'Processes', icon: Boxes },
  { path: '/pods', label: 'Pods', icon: Users2 },
  { path: '/roster', label: 'Roster', icon: Calendar },
  { path: '/conflicts', label: 'Conflicts', icon: AlertTriangle },
  { path: '/analytics', label: 'Analytics', icon: BarChart3 },
]

export default function Sidebar() {
  const location = useLocation()

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col">
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-xl font-bold">DataStraw</h1>
        <p className="text-sm text-slate-400">Roster Management</p>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </nav>

      <div className="p-4 border-t border-slate-700">
        <div className="text-sm text-slate-400">
          <p className="font-semibold">Operations Manager</p>
          <p className="text-xs">admin@datastraw.com</p>
        </div>
      </div>
    </aside>
  )
}
