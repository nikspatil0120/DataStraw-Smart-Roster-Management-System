import { useLocation } from 'react-router-dom'
import { Bell } from 'lucide-react'

const pageLabels: Record<string, string> = {
  '/': 'Dashboard',
  '/employees': 'Employees',
  '/brands': 'Brands',
  '/processes': 'Processes',
  '/pods': 'Pods',
  '/roster': 'Roster Management',
  '/conflicts': 'Scheduling Conflicts',
}

export default function Header() {
  const location = useLocation()
  const pageTitle = pageLabels[location.pathname] || 'Page'

  return (
    <header className="bg-white border-b border-slate-200 px-8 py-4 flex justify-between items-center">
      <h2 className="text-2xl font-bold text-slate-900">{pageTitle}</h2>
      <div className="flex items-center gap-4">
        <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors">
          <Bell size={24} className="text-slate-600" />
        </button>
      </div>
    </header>
  )
}
