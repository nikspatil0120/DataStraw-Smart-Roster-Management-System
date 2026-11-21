import { useQuery } from '@tanstack/react-query'
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { employeeAPI, brandAPI, processAPI, rosterAPI } from '../services/api'
import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [stats, setStats] = useState({
    employees: 0,
    brands: 0,
    processes: 0,
    rosters: 0,
  })

  const { data: employeesData } = useQuery({
    queryKey: ['employees'],
    queryFn: () => employeeAPI.list(0, 100),
  })

  const { data: brandsData } = useQuery({
    queryKey: ['brands'],
    queryFn: () => brandAPI.list(0, 100),
  })

  const { data: processesData } = useQuery({
    queryKey: ['processes'],
    queryFn: () => processAPI.list(),
  })

  const { data: rostersData } = useQuery({
    queryKey: ['rosters'],
    queryFn: () => rosterAPI.list(0, 100),
  })

  useEffect(() => {
    setStats({
      employees: employeesData?.data?.pagination?.total || 0,
      brands: brandsData?.data?.pagination?.total || 0,
      processes: processesData?.data?.pagination?.total || 0,
      rosters: rostersData?.data?.pagination?.total || 0,
    })
  }, [employeesData, brandsData, processesData, rostersData])

  const distributionData = [
    { name: 'Employees', value: stats.employees, color: '#0ea5e9' },
    { name: 'Brands', value: stats.brands, color: '#06b6d4' },
  ]

  const statusData = rostersData?.data?.data?.reduce(
    (acc: any, roster: any) => {
      const status = roster.status || 'unknown'
      const existing = acc.find((s: any) => s.name === status)
      if (existing) {
        existing.value += 1
      } else {
        acc.push({ name: status, value: 1 })
      }
      return acc
    },
    []
  ) || []

  return (
    <div className="space-y-8">
      {/* Metrics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-slate-600 text-sm font-medium">Total Employees</div>
          <div className="text-4xl font-bold text-slate-900 mt-2">{stats.employees}</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-slate-600 text-sm font-medium">Total Brands</div>
          <div className="text-4xl font-bold text-slate-900 mt-2">{stats.brands}</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-slate-600 text-sm font-medium">Processes</div>
          <div className="text-4xl font-bold text-slate-900 mt-2">{stats.processes}</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-slate-600 text-sm font-medium">Rosters</div>
          <div className="text-4xl font-bold text-slate-900 mt-2">{stats.rosters}</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-8">
        {/* Distribution */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Resource Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distributionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0' }} />
              <Bar dataKey="value" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Roster Status */}
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Roster Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry: any, index: number) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={['#0ea5e9', '#06b6d4', '#14b8a6', '#f59e0b'][index % 4]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Recent Rosters */}
      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Recent Rosters</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b border-slate-200">
              <tr>
                <th className="text-left text-sm font-semibold text-slate-700 pb-3 pl-4">Name</th>
                <th className="text-left text-sm font-semibold text-slate-700 pb-3">Month</th>
                <th className="text-left text-sm font-semibold text-slate-700 pb-3">Status</th>
                <th className="text-left text-sm font-semibold text-slate-700 pb-3">Version</th>
                <th className="text-left text-sm font-semibold text-slate-700 pb-3">Created</th>
              </tr>
            </thead>
            <tbody>
              {rostersData?.data?.data?.slice(0, 5).map((roster: any) => (
                <tr key={roster.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-3 pl-4 text-sm text-slate-900">{roster.roster_name}</td>
                  <td className="py-3 text-sm text-slate-600">{roster.month}/{roster.year}</td>
                  <td className="py-3 text-sm">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        roster.status === 'published'
                          ? 'bg-green-100 text-green-800'
                          : roster.status === 'generated'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-slate-100 text-slate-800'
                      }`}
                    >
                      {roster.status}
                    </span>
                  </td>
                  <td className="py-3 text-sm text-slate-600">{roster.version}</td>
                  <td className="py-3 text-sm text-slate-600">
                    {new Date(roster.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
