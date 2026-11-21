import { useQuery } from '@tanstack/react-query'
import { podAPI } from '../services/api'
import { Loader, AlertCircle } from 'lucide-react'

export default function Pods() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['pods'],
    queryFn: () => podAPI.list(0, 100)
  })

  const pods = data?.data?.data || []
  const totalCount = data?.data?.pagination?.total || 0

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Pods</h1>
        <p className="text-slate-600 mt-2">Manage operational pods and their team leads</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="text-red-600 mt-0.5 flex-shrink-0" size={20} />
          <div className="text-red-800">
            <p className="font-semibold">Failed to load pods</p>
            <p className="text-sm mt-1">{error instanceof Error ? error.message : 'Unknown error'}</p>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader className="text-blue-600 animate-spin" size={32} />
          <span className="ml-3 text-slate-600">Loading pods...</span>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 bg-slate-50 border-b">
            <p className="text-sm text-slate-600 font-medium">
              Showing {pods.length} of {totalCount} pods
            </p>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Pod ID</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Pod Name</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-700 uppercase tracking-wider">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {pods.map((pod: any) => (
                  <tr key={pod.id} className="hover:bg-slate-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-600">{pod.id.substring(0, 8)}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{pod.pod_name}</td>
                    <td className="px-6 py-4 text-sm text-slate-600">{pod.description || '-'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        pod.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {pod.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {new Date(pod.created_at).toLocaleDateString()}
                    </td>
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
