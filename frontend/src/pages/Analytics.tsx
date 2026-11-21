import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useState } from 'react'

const analyticsAPI = {
  dashboard: () => fetch('http://localhost:8000/api/analytics/dashboard').then(r => r.json()),
  coverage: () => fetch('http://localhost:8000/api/analytics/coverage').then(r => r.json()),
  workload: () => fetch('http://localhost:8000/api/analytics/workload').then(r => r.json()),
  conflicts: () => fetch('http://localhost:8000/api/analytics/conflicts').then(r => r.json()),
  assignments: () => fetch('http://localhost:8000/api/analytics/assignments').then(r => r.json()),
  pods: () => fetch('http://localhost:8000/api/analytics/pods').then(r => r.json()),
}

export default function Analytics() {
  const { data: dashboard } = useQuery({
    queryKey: ['analytics-dashboard'],
    queryFn: analyticsAPI.dashboard,
  })

  const { data: coverage } = useQuery({
    queryKey: ['analytics-coverage'],
    queryFn: analyticsAPI.coverage,
  })

  const { data: workload } = useQuery({
    queryKey: ['analytics-workload'],
    queryFn: analyticsAPI.workload,
  })

  const { data: conflicts } = useQuery({
    queryKey: ['analytics-conflicts'],
    queryFn: analyticsAPI.conflicts,
  })

  const { data: assignments } = useQuery({
    queryKey: ['analytics-assignments'],
    queryFn: analyticsAPI.assignments,
  })

  const { data: pods } = useQuery({
    queryKey: ['analytics-pods'],
    queryFn: analyticsAPI.pods,
  })

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs text-slate-600">Active Employees</div>
          <div className="text-2xl font-bold text-slate-900">{dashboard?.metrics?.active_employees}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs text-slate-600">Total Brands</div>
          <div className="text-2xl font-bold text-slate-900">{dashboard?.metrics?.total_brands}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs text-slate-600">Published Rosters</div>
          <div className="text-2xl font-bold text-slate-900">{dashboard?.metrics?.published_rosters}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs text-slate-600">Critical Conflicts</div>
          <div className="text-2xl font-bold text-red-600">{dashboard?.metrics?.critical_conflicts}</div>
        </div>
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
          <div className="text-xs text-slate-600">Pending Leaves</div>
          <div className="text-2xl font-bold text-slate-900">{dashboard?.metrics?.pending_leaves}</div>
        </div>
      </div>

      {/* Coverage & Distribution */}
      <div className="grid grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Coverage Status</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Working', value: coverage?.coverage?.working || 0 },
                  { name: 'Leave', value: coverage?.coverage?.on_leave || 0 },
                  { name: 'Weekly Off', value: coverage?.coverage?.weekly_off || 0 },
                  { name: 'Unavailable', value: coverage?.coverage?.unavailable || 0 },
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                <Cell fill="#0ea5e9" />
                <Cell fill="#14b8a6" />
                <Cell fill="#f59e0b" />
                <Cell fill="#ef4444" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Brand Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={assignments?.assignments?.distribution || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                <Cell fill="#0ea5e9" />
                <Cell fill="#06b6d4" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Workload Distribution */}
      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Top Workload Distribution (Last 30 Days)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={workload?.workload?.employees || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="assignments" fill="#0ea5e9" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Conflicts Breakdown */}
      <div className="grid grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Conflicts by Severity</h3>
          <div className="space-y-2">
            {Object.entries(conflicts?.conflicts?.by_severity || {}).map(([severity, count]: any) => (
              <div key={severity} className="flex justify-between items-center">
                <span className="text-sm text-slate-600 capitalize">{severity}</span>
                <span className={`font-bold px-3 py-1 rounded text-sm ${
                  severity === 'critical' ? 'bg-red-100 text-red-800' :
                  severity === 'high' ? 'bg-orange-100 text-orange-800' :
                  severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-slate-100 text-slate-800'
                }`}>
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Resolution Rate</h3>
          <div className="text-center py-8">
            <div className="text-5xl font-bold text-primary-600 mb-2">
              {conflicts?.conflicts?.resolution_rate}%
            </div>
            <p className="text-sm text-slate-600">
              {conflicts?.conflicts?.resolved_conflicts} / {conflicts?.conflicts?.total_conflicts} resolved
            </p>
          </div>
        </div>
      </div>

      {/* Pod Summary */}
      <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Pod Overview</h3>
        <div className="grid grid-cols-2 gap-4">
          {pods?.pods?.map((pod: any) => (
            <div key={pod.pod_name} className="p-4 border border-slate-200 rounded-lg">
              <h4 className="font-semibold text-slate-900">{pod.pod_name}</h4>
              <div className="mt-3 space-y-1 text-sm text-slate-600">
                <p>👤 Employees: <span className="font-bold text-slate-900">{pod.employees}</span></p>
                <p>📋 Assignments: <span className="font-bold text-slate-900">{pod.assignments}</span></p>
                <p>👔 Lead: <span className="font-bold text-slate-900">{pod.pod_lead}</span></p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
