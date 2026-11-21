import { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { schedulingAPI, rosterAPI, conflictAPI } from '../services/api'
import { Calendar, AlertTriangle, CheckCircle, Loader, ChevronLeft, ChevronRight, Zap, Users, Briefcase, TrendingUp } from 'lucide-react'

export default function Roster() {
  const [month, setMonth] = useState(new Date().getMonth() + 1)
  const [year, setYear] = useState(new Date().getFullYear())
  const [selectedRoster, setSelectedRoster] = useState<string | null>(null)
  const [rosterName, setRosterName] = useState(`Roster ${month}/${year}`)
  const [entriesPage, setEntriesPage] = useState(1)
  const entriesPerPage = 50
  const [hoveredRow, setHoveredRow] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch all rosters
  const { data: rostersListData, refetch: refetchRosters } = useQuery({
    queryKey: ['rosters-list'],
    queryFn: () => rosterAPI.list(0, 100)
  })

  // Auto-select the most recent roster on load
  useEffect(() => {
    if (rostersListData?.data?.data && !selectedRoster) {
      const latest = rostersListData.data.data[0]
      if (latest) {
        setSelectedRoster(latest.id)
        setMonth(latest.month)
        setYear(latest.year)
        setRosterName(latest.roster_name)
      }
    }
  }, [rostersListData, selectedRoster])

  // Generate roster mutation
  const generateMutation = useMutation({
    mutationFn: () => schedulingAPI.generate(rosterName, month, year),
    onSuccess: (data) => {
      setSelectedRoster(data.data.roster_id)
      setError(null)
      refetchRosters()
    },
    onError: (err: Error) => {
      setError(err.message)
    }
  })

  // Publish mutation
  const publishMutation = useMutation({
    mutationFn: () => (selectedRoster ? rosterAPI.publish(selectedRoster) : Promise.reject()),
    onSuccess: () => {
      setError(null)
      refetchRosters()
    },
    onError: (err: Error) => {
      setError(err.message)
    }
  })

  // Roster queries
  const { data: rosterData, refetch: refetchRosterDetail } = useQuery({
    queryKey: ['rosters', selectedRoster],
    queryFn: () => (selectedRoster ? rosterAPI.get(selectedRoster) : Promise.reject()),
    enabled: !!selectedRoster,
  })

  const { data: entriesData, isLoading: entriesLoading } = useQuery({
    queryKey: ['roster-entries', selectedRoster],
    queryFn: () => (selectedRoster ? rosterAPI.entries(selectedRoster, 0, 1000) : Promise.reject()),
    enabled: !!selectedRoster,
  })

  const { data: conflictsData } = useQuery({
    queryKey: ['roster-conflicts', selectedRoster],
    queryFn: () => (selectedRoster ? conflictAPI.summary(selectedRoster) : Promise.reject()),
    enabled: !!selectedRoster,
  })

  const { data: coverageData } = useQuery({
    queryKey: ['roster-coverage', selectedRoster],
    queryFn: () => (selectedRoster ? rosterAPI.coverage(selectedRoster) : Promise.reject()),
    enabled: !!selectedRoster,
  })

  const handleGenerate = () => {
    generateMutation.mutate()
  }

  const handlePublish = () => {
    if (conflictsData?.data?.summary?.can_publish) {
      publishMutation.mutate()
    }
  }

  const entries = entriesData?.data?.data || []
  const totalEntries = entries.length
  const totalPages = Math.ceil(totalEntries / entriesPerPage)
  const startIdx = (entriesPage - 1) * entriesPerPage
  const endIdx = Math.min(startIdx + entriesPerPage, totalEntries)
  const paginatedEntries = entries.slice(startIdx, endIdx)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 p-8 overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-gradient-to-br from-cyan-500/20 to-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="max-w-7xl mx-auto space-y-8 relative z-10">
        {/* Premium Header */}
        <div className="mb-12 group">
          <div className="flex items-center gap-4 mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-2xl blur-xl opacity-75 group-hover:opacity-100 transition-all duration-500"></div>
              <div className="relative p-4 bg-gradient-to-br from-blue-500 via-cyan-500 to-purple-500 rounded-2xl shadow-2xl">
                <Zap className="text-white" size={28} />
              </div>
            </div>
            <div>
              <h1 className="text-5xl font-black text-white bg-gradient-to-r from-blue-200 via-cyan-200 to-purple-200 bg-clip-text text-transparent">
                Roster Management
              </h1>
              <p className="text-slate-300 text-base mt-2 font-medium">Generate, publish, and manage monthly rosters with AI-powered scheduling</p>
            </div>
          </div>
        </div>

        {/* Global Error Banner */}
        {error && (
          <div className="p-6 bg-gradient-to-r from-red-900/40 via-red-900/30 to-orange-900/40 rounded-2xl border border-red-700/50 flex items-start gap-4 backdrop-blur-sm shadow-lg animate-in">
            <AlertTriangle size={24} className="text-red-300 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-base font-bold text-red-200">⚠️ Operation Error</p>
              <p className="text-sm text-red-300 mt-2">{error}</p>
            </div>
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-300 hover:text-red-200 hover:bg-red-900/30 px-4 py-2 rounded-lg transition-all font-bold"
            >
              ✕
            </button>
          </div>
        )}

        {/* Generate Section - Premium Card */}
        <div className="group relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/30 to-cyan-600/30 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
          <div className="relative bg-gradient-to-br from-slate-800/80 via-slate-800/40 to-slate-900/80 backdrop-blur-2xl border border-slate-700/30 hover:border-slate-600/50 p-10 rounded-3xl shadow-2xl transition-all duration-300 group-hover:shadow-3xl">
            <h2 className="text-3xl font-black text-white mb-8 flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl">
                <Calendar size={24} className="text-white" />
              </div>
              <span className="bg-gradient-to-r from-blue-200 to-cyan-200 bg-clip-text text-transparent">Generate New Roster</span>
            </h2>
            <div className="grid grid-cols-5 gap-4">
              <div className="group/input">
                <label className="text-xs font-bold text-slate-300 block mb-3 uppercase tracking-wider">Roster Name</label>
                <input
                  type="text"
                  value={rosterName}
                  onChange={(e) => setRosterName(e.target.value)}
                  className="w-full px-5 py-3 bg-slate-700/30 border border-slate-600/40 hover:border-slate-500/60 focus:border-blue-500/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-white placeholder-slate-500 transition-all duration-300 backdrop-blur"
                  placeholder="Roster name"
                />
              </div>
              <div className="group/input">
                <label className="text-xs font-bold text-slate-300 block mb-3 uppercase tracking-wider">Month</label>
                <select
                  value={month}
                  onChange={(e) => setMonth(parseInt(e.target.value))}
                  className="w-full px-5 py-3 bg-slate-700/30 border border-slate-600/40 hover:border-slate-500/60 focus:border-blue-500/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-white transition-all duration-300 backdrop-blur"
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((m) => (
                    <option key={m} value={m} className="bg-slate-700">{m}</option>
                  ))}
                </select>
              </div>
              <div className="group/input">
                <label className="text-xs font-bold text-slate-300 block mb-3 uppercase tracking-wider">Year</label>
                <select
                  value={year}
                  onChange={(e) => setYear(parseInt(e.target.value))}
                  className="w-full px-5 py-3 bg-slate-700/30 border border-slate-600/40 hover:border-slate-500/60 focus:border-blue-500/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 text-white transition-all duration-300 backdrop-blur"
                >
                  {[2023, 2024, 2025, 2026].map((y) => (
                    <option key={y} value={y} className="bg-slate-700">{y}</option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleGenerate}
                  disabled={generateMutation.isPending}
                  className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:from-blue-700 hover:via-blue-600 hover:to-cyan-600 text-white rounded-xl font-bold disabled:opacity-50 transition-all transform hover:scale-105 active:scale-95 shadow-xl hover:shadow-2xl duration-300 uppercase text-sm tracking-wider"
                >
                  {generateMutation.isPending ? (
                    <div className="flex items-center justify-center gap-2">
                      <Loader size={18} className="animate-spin" />
                      Generating...
                    </div>
                  ) : (
                    '✨ Generate Roster'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Rosters - Premium Table */}
        {rostersListData?.data?.data && rostersListData.data.data.length > 0 && (
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/30 to-pink-600/30 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
            <div className="relative bg-gradient-to-br from-slate-800/80 via-slate-800/40 to-slate-900/80 backdrop-blur-2xl border border-slate-700/30 hover:border-slate-600/50 p-10 rounded-3xl shadow-2xl transition-all duration-300">
              <h3 className="text-3xl font-black text-white mb-8 bg-gradient-to-r from-purple-200 to-pink-200 bg-clip-text text-transparent">Recent Rosters</h3>
              <div className="overflow-x-auto rounded-2xl border border-slate-700/30">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 border-b border-slate-700/30">
                      <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Name</th>
                      <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Month</th>
                      <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Status</th>
                      <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Version</th>
                      <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Created</th>
                      <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/30">
                    {rostersListData.data.data.map((roster: any) => (
                      <tr
                        key={roster.id}
                        onMouseEnter={() => setHoveredRow(roster.id)}
                        onMouseLeave={() => setHoveredRow(null)}
                        className={`transition-all duration-300 ${
                          selectedRoster === roster.id 
                            ? 'bg-gradient-to-r from-blue-900/40 to-cyan-900/40 border-l-4 border-blue-500' 
                            : hoveredRow === roster.id
                            ? 'bg-slate-700/40'
                            : 'hover:bg-slate-700/20'
                        }`}
                      >
                        <td className="py-5 px-6 font-semibold text-white">{roster.roster_name}</td>
                        <td className="py-5 px-6 text-slate-300 font-mono">{roster.month}/{roster.year}</td>
                        <td className="py-5 px-6">
                          <span
                            className={`px-4 py-2 rounded-full text-xs font-bold transition-all ${
                              roster.status === 'published'
                                ? 'bg-gradient-to-r from-green-900/40 to-emerald-900/40 text-green-300 border border-green-700/50'
                                : roster.status === 'validated'
                                ? 'bg-gradient-to-r from-blue-900/40 to-cyan-900/40 text-blue-300 border border-blue-700/50'
                                : 'bg-slate-700/40 text-slate-300 border border-slate-600/50'
                            }`}
                          >
                            {roster.status}
                          </span>
                        </td>
                        <td className="py-5 px-6 text-slate-300 font-mono">v{roster.version}</td>
                        <td className="py-5 px-6 text-slate-300 text-sm">{new Date(roster.created_at).toLocaleDateString()}</td>
                        <td className="py-5 px-6">
                          <button
                            onClick={() => {
                              setSelectedRoster(roster.id)
                              setMonth(roster.month)
                              setYear(roster.year)
                              setRosterName(roster.roster_name)
                              setEntriesPage(1)
                            }}
                            className={`px-5 py-2 rounded-xl text-sm font-bold transition-all transform hover:scale-105 ${
                              selectedRoster === roster.id
                                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg'
                                : 'bg-slate-700/50 text-slate-200 hover:bg-slate-600'
                            }`}
                          >
                            {selectedRoster === roster.id ? '✓ Selected' : 'View'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Roster Summary Cards - Premium */}
        {selectedRoster && rosterData && (
          <div className="grid grid-cols-4 gap-6">
            {[
              {
                label: 'Roster Status',
                value: rosterData.data.status,
                icon: rosterData.data.status === 'published' ? CheckCircle : Calendar,
                gradient: 'from-blue-600/20 to-cyan-600/20',
                borderColor: 'border-blue-500/30',
                textGradient: 'from-blue-300 to-cyan-300'
              },
              {
                label: 'Coverage',
                value: `${coverageData?.data?.coverage?.coverage_percentage || 0}%`,
                icon: TrendingUp,
                gradient: 'from-purple-600/20 to-pink-600/20',
                borderColor: 'border-purple-500/30',
                textGradient: 'from-purple-300 to-pink-300'
              },
              {
                label: 'Roster Entries',
                value: totalEntries,
                icon: Briefcase,
                gradient: 'from-emerald-600/20 to-teal-600/20',
                borderColor: 'border-emerald-500/30',
                textGradient: 'from-emerald-300 to-teal-300'
              },
              {
                label: 'Critical Issues',
                value: conflictsData?.data?.summary?.total_conflicts || 0,
                icon: AlertTriangle,
                gradient: 'from-red-600/20 to-orange-600/20',
                borderColor: 'border-red-500/30',
                textGradient: 'from-red-300 to-orange-300'
              }
            ].map((card, idx) => {
              const Icon = card.icon
              return (
                <div key={idx} className="group relative">
                  <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500`}></div>
                  <div className={`relative bg-gradient-to-br ${card.gradient} backdrop-blur-2xl border ${card.borderColor} p-8 rounded-2xl shadow-xl transition-all duration-300 group-hover:shadow-2xl group-hover:border-opacity-50`}>
                    <div className="flex items-start justify-between mb-4">
                      <p className="text-xs font-bold text-slate-300 uppercase tracking-wider">{card.label}</p>
                      <Icon className={`text-opacity-60 group-hover:text-opacity-100 transition-all w-5 h-5 bg-gradient-to-br ${card.textGradient} bg-clip-text text-transparent`} />
                    </div>
                    <p className={`text-4xl font-black bg-gradient-to-r ${card.textGradient} bg-clip-text text-transparent`}>{card.value}</p>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Conflict Summary - Premium */}
        {selectedRoster && conflictsData && (
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-red-600/30 to-orange-600/30 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
            <div className="relative bg-gradient-to-br from-slate-800/80 via-slate-800/40 to-slate-900/80 backdrop-blur-2xl border border-slate-700/30 hover:border-slate-600/50 p-10 rounded-3xl shadow-2xl transition-all duration-300">
              <h3 className="text-3xl font-black text-white mb-8 flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-red-500 to-orange-500 rounded-xl">
                  <AlertTriangle size={24} className="text-white" />
                </div>
                <span className="bg-gradient-to-r from-red-200 to-orange-200 bg-clip-text text-transparent">Conflict Summary</span>
              </h3>
              <div className="grid grid-cols-5 gap-4 mb-10">
                {[
                  { label: 'Total', value: conflictsData.data.summary.total_conflicts, color: 'from-slate-600 to-slate-500' },
                  { label: 'Critical', value: conflictsData.data.summary.by_severity.critical, color: 'from-red-600 to-red-500' },
                  { label: 'High', value: conflictsData.data.summary.by_severity.high, color: 'from-orange-600 to-orange-500' },
                  { label: 'Medium', value: conflictsData.data.summary.by_severity.medium, color: 'from-yellow-600 to-yellow-500' },
                  { label: 'Low', value: conflictsData.data.summary.by_severity.low, color: 'from-green-600 to-green-500' },
                ].map((item) => (
                  <div key={item.label} className="group/stat relative">
                    <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover/stat:opacity-100 rounded-xl blur transition-all duration-300"></div>
                    <div className="relative bg-slate-700/40 backdrop-blur border border-slate-600/30 hover:border-slate-500/50 p-6 rounded-xl transition-all duration-300 hover:shadow-lg">
                      <p className="text-slate-400 text-xs font-bold uppercase mb-3 tracking-wider">{item.label}</p>
                      <p className={`text-4xl font-black bg-gradient-to-r ${item.color} bg-clip-text text-transparent`}>{item.value}</p>
                    </div>
                  </div>
                ))}
              </div>

              <button
                onClick={handlePublish}
                disabled={!conflictsData.data.summary.can_publish || publishMutation.isPending}
                className={`w-full px-8 py-5 rounded-xl font-bold text-lg transition-all transform hover:scale-105 active:scale-95 shadow-2xl uppercase tracking-wider ${
                  conflictsData.data.summary.can_publish
                    ? 'bg-gradient-to-r from-green-600 via-green-500 to-emerald-600 hover:from-green-700 hover:via-green-600 hover:to-emerald-700 text-white hover:shadow-3xl'
                    : 'bg-slate-600 text-slate-400 cursor-not-allowed opacity-60'
                }`}
              >
                {publishMutation.isPending ? (
                  <div className="flex items-center justify-center gap-3">
                    <Loader size={20} className="animate-spin" />
                    Publishing Roster...
                  </div>
                ) : (
                  '🚀 Publish Roster'
                )}
              </button>
            </div>
          </div>
        )}

        {/* Entries Table with Premium Pagination */}
        {selectedRoster && entriesData && (
          <div className="group relative">
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-600/30 to-blue-600/30 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
            <div className="relative bg-gradient-to-br from-slate-800/80 via-slate-800/40 to-slate-900/80 backdrop-blur-2xl border border-slate-700/30 hover:border-slate-600/50 p-10 rounded-3xl shadow-2xl transition-all duration-300">
              <div className="flex items-center justify-between mb-8">
                <h3 className="text-3xl font-black text-white">
                  Roster Entries
                  <span className="ml-3 text-transparent bg-gradient-to-r from-cyan-300 to-blue-300 bg-clip-text">({totalEntries})</span>
                </h3>
                <div className="text-sm font-semibold text-slate-300 bg-slate-700/40 px-6 py-3 rounded-xl border border-slate-600/30">
                  Page <span className="text-white mx-1">{entriesPage}</span> of <span className="text-white mx-1">{totalPages}</span> • 
                  <span className="text-white ml-2">{startIdx + 1}-{endIdx}</span> of <span className="text-white ml-1">{totalEntries}</span>
                </div>
              </div>

              {entriesLoading ? (
                <div className="flex items-center justify-center py-24">
                  <Loader className="animate-spin text-blue-400 mr-4" size={32} />
                  <span className="text-slate-300 text-lg font-semibold">Loading entries...</span>
                </div>
              ) : paginatedEntries.length === 0 ? (
                <div className="py-24 text-center text-slate-400 text-lg">No entries found</div>
              ) : (
                <>
                  <div className="overflow-x-auto rounded-2xl border border-slate-700/30 mb-8 bg-slate-800/30">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="bg-gradient-to-r from-slate-800/50 to-slate-700/50 border-b border-slate-700/30 sticky top-0">
                          <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">#</th>
                          <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Date</th>
                          <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Employee</th>
                          <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Brand</th>
                          <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Process</th>
                          <th className="text-left py-5 px-6 font-bold text-slate-200 uppercase text-xs tracking-wider">Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-700/30">
                        {paginatedEntries.map((entry: any, idx: number) => (
                          <tr 
                            key={entry.id} 
                            className="hover:bg-slate-700/40 transition-all duration-200 group/row"
                          >
                            <td className="py-5 px-6 text-slate-400 font-bold text-sm">#{startIdx + idx + 1}</td>
                            <td className="py-5 px-6 text-white font-semibold">{entry.roster_date}</td>
                            <td className="py-5 px-6 text-slate-300 font-mono text-xs bg-slate-700/20 px-3 py-1 rounded-lg w-fit">{entry.employee_id?.slice(0, 8)}</td>
                            <td className="py-5 px-6 text-slate-300 font-mono text-xs bg-slate-700/20 px-3 py-1 rounded-lg w-fit">{entry.brand_id?.slice(0, 8)}</td>
                            <td className="py-5 px-6 text-slate-300 font-mono text-xs">{entry.process_id?.slice(0, 8) || '-'}</td>
                            <td className="py-5 px-6">
                              <span className="px-4 py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-green-900/40 to-emerald-900/40 text-green-300 border border-green-700/50 inline-block">
                                ✓ {entry.assignment_status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Premium Pagination Controls */}
                  {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-6 pt-10 border-t border-slate-700/30">
                      <button
                        onClick={() => setEntriesPage(Math.max(1, entriesPage - 1))}
                        disabled={entriesPage === 1}
                        className="p-3 rounded-xl bg-slate-700/40 hover:bg-slate-700/60 disabled:opacity-30 disabled:cursor-not-allowed text-slate-300 hover:text-white transition-all transform hover:scale-110 border border-slate-600/30"
                      >
                        <ChevronLeft size={22} />
                      </button>

                      <div className="flex gap-3">
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          let page;
                          if (totalPages <= 5) {
                            page = i + 1;
                          } else if (entriesPage <= 3) {
                            page = i + 1;
                          } else if (entriesPage >= totalPages - 2) {
                            page = totalPages - 4 + i;
                          } else {
                            page = entriesPage - 2 + i;
                          }
                          return (
                            <button
                              key={page}
                              onClick={() => setEntriesPage(page)}
                              className={`w-12 h-12 rounded-xl font-bold transition-all transform hover:scale-110 ${
                                entriesPage === page
                                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/50'
                                  : 'bg-slate-700/40 text-slate-300 hover:bg-slate-700/60 border border-slate-600/30'
                              }`}
                            >
                              {page}
                            </button>
                          );
                        })}
                      </div>

                      <button
                        onClick={() => setEntriesPage(Math.min(totalPages, entriesPage + 1))}
                        disabled={entriesPage === totalPages}
                        className="p-3 rounded-xl bg-slate-700/40 hover:bg-slate-700/60 disabled:opacity-30 disabled:cursor-not-allowed text-slate-300 hover:text-white transition-all transform hover:scale-110 border border-slate-600/30"
                      >
                        <ChevronRight size={22} />
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
