import { useQuery } from '@tanstack/react-query'
import { employeeAPI } from '../services/api'
import { Loader, AlertCircle } from 'lucide-react'

export default function Employees() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['employees'],
    queryFn: () => employeeAPI.list(0, 100)
  })

  const employees = data?.data?.data || []
  const totalCount = data?.data?.pagination?.total || 0

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Employees</h1>
        <p className="text-slate-600 mt-2">Manage employee information and assignments</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="text-red-600 mt-0.5 flex-shrink-0" size={20} />
          <div className="text-red-800">
            <p className="font-semibold">Failed to load employees</p>
            <p className="text-sm mt-1">{error instanceof Error ? error.message : 'Unknown error'}</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="text-blue-600 animate-spin" size={32} />
          <span className="ml-3 text-slate-600">Loading employees...</span>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 bg-slate-50 border-b">
            <p className="text-sm text-slate-600 font-medium">
              Showing {employees.length} of {totalCount} employees
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Name</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Email</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Phone</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Role</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Weekly Off</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {employees.map((emp: any) => (
                  <tr key={emp.id} className="hover:bg-slate-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{emp.employee_code}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">{emp.full_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{emp.email}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{emp.phone}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        emp.role === 'pod_lead' 
                          ? 'bg-purple-100 text-purple-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {emp.role.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        emp.employment_status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {emp.employment_status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{emp.preferred_weekly_off || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
