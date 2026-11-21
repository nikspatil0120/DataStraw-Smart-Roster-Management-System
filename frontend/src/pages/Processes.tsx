import { useQuery } from '@tanstack/react-query'
import { processAPI } from '../services/api'
import { Loader, AlertCircle } from 'lucide-react'

export default function Processes() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['processes'],
    queryFn: () => processAPI.list()
  })

  const processes = data?.data?.data || []
  const totalCount = data?.data?.pagination?.total || 0

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Processes</h1>
        <p className="text-slate-600 mt-2">Manage operational processes and workflows</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="text-red-600 mt-0.5 flex-shrink-0" size={20} />
          <div className="text-red-800">
            <p className="font-semibold">Failed to load processes</p>
            <p className="text-sm mt-1">{error instanceof Error ? error.message : 'Unknown error'}</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="text-blue-600 animate-spin" size={32} />
          <span className="ml-3 text-slate-600">Loading processes...</span>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 bg-slate-50 border-b">
            <p className="text-sm text-slate-600 font-medium">
              Showing {processes.length} of {totalCount} processes
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Process ID</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Process Name</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Level</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {processes.map((process: any) => (
                  <tr key={process.id} className="hover:bg-slate-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-600">{process.id.substring(0, 8)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{process.process_name}</td>
                    <td className="px-6 py-4 text-sm text-slate-600">{process.description || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        process.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {process.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{process.seniority_level || '-'}</td>
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
