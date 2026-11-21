import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { rosterAPI, conflictAPI } from '../services/api'
import { AlertTriangle, CheckCircle, Loader, ChevronLeft, ChevronRight, Shield, Zap, TrendingDown } from 'lucide-react'

export default function Conflicts() {
  const [selectedRoster, setSelectedRoster] = useState<string | null>(null)
  const [severity, setSeverity] = useState<string | null>(null)
  const [resolvedConflicts, setResolvedConflicts] = useState<Set<string>>(new Set())
  const [conflictsPage, setConflictsPage] = useState(1)
  const conflictsPerPage = 10
  const [hoveredConflict, setHoveredConflict] = useState<string | null>(null)
  const [error, setError] = useState<{ conflictId: string; message: string } | null>(null)

  // Get rosters
  const { data: rostersData } = useQuery({
    queryKey: ['rosters'],
    queryFn: () => rosterAPI.list(0, 100),
  })

  // Get conflicts for selected roster
  const { data: conflictsData, refetch: refetchConflicts } = useQuery({
    queryKey: ['conflicts', selectedRoster, severity],
    queryFn: () =>
      selectedRoster ? conflictAPI.list(selectedRoster, 0, 100) : Promise.reject(),
    enabled: !!selectedRoster,
  })

  // Resolve conflict mutation
  const resolveMutation = useMutation({
    mutationFn: async (conflictId: string) => {
      const response = await fetch(`http://localhost:8000/api/conflicts/${conflictId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        const errorMessage = errorData.detail || errorData.message || `HTTP ${response.status} Error`
        throw new Error(errorMessage)
      }
      
      const data = await response.json()
      return data.conflict
    },
    onSuccess: (data) => {
      setResolvedConflicts(prev => new Set([...prev, data.id]))
      setError(null)
      refetchConflicts()
    },
    onError: (err: Error, conflictId: string) => {
      setError({
        conflictId,
        message: err.message
      })
      console.error('Failed to resolve conflict:', err)
    }
  })

  const handleResolve = (conflictId: string) => {
    resolveMutation.mutate(conflictId)
  }

  const filtered = conflictsData?.data?.data?.filter(
    (c: any) => !severity || c.severity === severity
  ) || []

  const totalConflicts = filtered.length
  const totalPages = Math.ceil(totalConflicts / conflictsPerPage)
  const startIdx = (conflictsPage - 1) * conflictsPerPage
  const endIdx = Math.min(startIdx + conflictsPerPage, totalConflicts)
  const paginatedConflicts = filtered.slice(startIdx, endIdx)
  const resolvedCount = filtered.filter((c: any) => c.resolved || resolvedConflicts.has(c.id)).length

  const severityConfig: Record<string, { color: string; bgColor: string; icon: string }> = {
    critical: { color: 'text-red-400', bgColor: 'bg-red-900/20 border-red-700/30', icon: '🔴' },
    high: { color: 'text-orange-400', bgColor: 'bg-orange-900/20 border-orange-700/30', icon: '🟠' },
    medium: { color: 'text-yellow-400', bgColor: 'bg-yellow-900/20 border-yellow-700/30', icon: '🟡' },
    low: { color: 'text-green-400', bgColor: 'bg-green-900/20 border-green-700/30', icon: '🟢' },
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-red-950 to-slate-950 p-8 overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-gradient-to-br from-red-500/20 to-pink-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-gradient-to-br from-orange-500/20 to-red-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      <div className="max-w-7xl mx-auto space-y-8 relative z-10">
        {/* Premium Header */}
        <div className="mb-12 group">
          <div className="flex items-center gap-4 mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl blur-xl opacity-75 group-hover:opacity-100 transition-all duration-500"></div>
              <div className="relative p-4 bg-gradient-to-br from-red-500 via-pink-500 to-orange-500 rounded-2xl shadow-2xl">
                <Shield className="text-white" size={28} />
              </div>
            </div>
            <div>
              <h1 className="text-5xl font-black text-white bg-gradient-to-r from-red-200 via-pink-200 to-orange-200 bg-clip-text text-transparent">
                Scheduling Conflicts
              </h1>
              <p className="text-slate-300 text-base mt-2 font-medium">Detect, analyze, and intelligently resolve scheduling conflicts</p>
            </div>
          </div>
        </div>

        {/* Filters - Premium Card */}
        <div className="group relative">
          <div className="absolute inset-0 bg-gradient-to-r from-red-600/30 to-orange-600/30 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
          <div className="relative bg-gradient-to-br from-slate-800/80 via-slate-800/40 to-slate-900/80 backdrop-blur-2xl border border-slate-700/30 hover:border-slate-600/50 p-10 rounded-3xl shadow-2xl transition-all duration-300">
            <h2 className="text-3xl font-black text-white mb-8 bg-gradient-to-r from-red-200 to-orange-200 bg-clip-text text-transparent">Filter Conflicts</h2>
            <div className="grid grid-cols-2 gap-6">
              <div className="group/input">
                <label className="text-xs font-bold text-slate-300 block mb-3 uppercase tracking-wider">Select Roster</label>
                <select
                  value={selectedRoster || ''}
                  onChange={(e) => {
                    setSelectedRoster(e.target.value || null)
                    setConflictsPage(1)
                  }}
                  className="w-full px-5 py-3 bg-slate-700/30 border border-slate-600/40 hover:border-slate-500/60 focus:border-red-500/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 text-white placeholder-slate-500 transition-all duration-300 backdrop-blur"
                >
                  <option value="">Select a roster...</option>
                  {rostersData?.data?.data?.map((r: any) => (
                    <option key={r.id} value={r.id} className="bg-slate-700">
                      {r.roster_name} ({r.month}/{r.year})
                    </option>
                  ))}
                </select>
              </div>
              <div className="group/input">
                <label className="text-xs font-bold text-slate-300 block mb-3 uppercase tracking-wider">Severity Filter</label>
                <select
                  value={severity || ''}
                  onChange={(e) => {
                    setSeverity(e.target.value || null)
                    setConflictsPage(1)
                  }}
                  className="w-full px-5 py-3 bg-slate-700/30 border border-slate-600/40 hover:border-slate-500/60 focus:border-red-500/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 text-white transition-all duration-300 backdrop-blur"
                >
                  <option value="" className="bg-slate-700">All Severities</option>
                  <option value="critical" className="bg-slate-700">🔴 Critical</option>
                  <option value="high" className="bg-slate-700">🟠 High</option>
                  <option value="medium" className="bg-slate-700">🟡 Medium</option>
                  <option value="low" className="bg-slate-700">🟢 Low</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Conflicts Summary Cards - Premium */}
        {selectedRoster && (
          <div className="grid grid-cols-3 gap-6">
            {[
              {
                label: 'Total Conflicts',
                value: totalConflicts,
                gradient: 'from-slate-600/20 to-slate-500/20',
                borderColor: 'border-slate-500/30',
                textGradient: 'from-slate-300 to-slate-200',
                icon: AlertTriangle
              },
              {
                label: 'Resolved',
                value: resolvedCount,
                percentage: Math.round((resolvedCount / totalConflicts) * 100),
                gradient: 'from-green-600/20 to-emerald-600/20',
                borderColor: 'border-green-500/30',
                textGradient: 'from-green-300 to-emerald-300',
                icon: CheckCircle
              },
              {
                label: 'Remaining',
                value: totalConflicts - resolvedCount,
                percentage: Math.round(((totalConflicts - resolvedCount) / totalConflicts) * 100),
                gradient: 'from-red-600/20 to-orange-600/20',
                borderColor: 'border-red-500/30',
                textGradient: 'from-red-300 to-orange-300',
                icon: TrendingDown
              }
            ].map((card, idx) => {
              const Icon = card.icon
              return (
                <div key={idx} className="group relative">
                  <div className={`absolute inset-0 bg-gradient-to-br ${card.gradient} rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-all duration-500`}></div>
                  <div className={`relative bg-gradient-to-br ${card.gradient} backdrop-blur-2xl border ${card.borderColor} p-8 rounded-2xl shadow-xl transition-all duration-300 group-hover:shadow-2xl`}>
                    <div className="flex items-start justify-between mb-6">
                      <p className="text-xs font-bold text-slate-300 uppercase tracking-wider">{card.label}</p>
                      <Icon className={`w-5 h-5 bg-gradient-to-br ${card.textGradient} bg-clip-text text-transparent`} />
                    </div>
                    <div className="flex items-end gap-3">
                      <p className={`text-5xl font-black bg-gradient-to-r ${card.textGradient} bg-clip-text text-transparent`}>{card.value}</p>
                      {card.percentage !== undefined && (
                        <p className={`text-lg font-bold bg-gradient-to-r ${card.textGradient} bg-clip-text text-transparent mb-1`}>({card.percentage}%)</p>
                      )}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Conflicts List - Premium */}
        <div className="group relative">
          <div className="absolute inset-0 bg-gradient-to-r from-red-600/30 to-pink-600/30 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
          <div className="relative bg-gradient-to-br from-slate-800/80 via-slate-800/40 to-slate-900/80 backdrop-blur-2xl border border-slate-700/30 hover:border-slate-600/50 p-10 rounded-3xl shadow-2xl transition-all duration-300">
            {/* Global Error Banner */}
            {error && (
              <div className="mb-8 p-5 bg-gradient-to-r from-red-900/40 via-red-900/30 to-orange-900/40 rounded-2xl border border-red-700/50 flex items-start gap-4 backdrop-blur-sm shadow-lg">
                <AlertTriangle size={24} className="text-red-300 flex-shrink-0 mt-1" />
                <div className="flex-1">
                  <p className="text-base font-bold text-red-200">⚠️ Resolution Error</p>
                  <p className="text-sm text-red-300 mt-2">Failed to resolve conflict: <span className="font-mono text-red-200">{error.message}</span></p>
                  <p className="text-xs text-red-400 mt-3">Please check your connection or try again later.</p>
                </div>
                <button
                  onClick={() => setError(null)}
                  className="ml-4 text-red-300 hover:text-red-200 hover:bg-red-900/30 px-3 py-1 rounded-lg transition-all"
                >
                  ✕
                </button>
              </div>
            )}

            <div className="flex items-center justify-between mb-8">
              <h3 className="text-3xl font-black text-white">
                Conflicts List
                <span className="ml-3 text-transparent bg-gradient-to-r from-red-300 to-pink-300 bg-clip-text">({totalConflicts})</span>
              </h3>
              {selectedRoster && (
                <div className="text-sm font-semibold text-slate-300 bg-slate-700/40 px-6 py-3 rounded-xl border border-slate-600/30">
                  Page <span className="text-white mx-1">{conflictsPage}</span> of <span className="text-white mx-1">{Math.max(1, totalPages)}</span> • 
                  <span className="text-white ml-2">{totalConflicts > 0 ? startIdx + 1 : 0}-{endIdx}</span> of <span className="text-white ml-1">{totalConflicts}</span>
                </div>
              )}
            </div>

            {!selectedRoster ? (
              <div className="py-24 text-center">
                <AlertTriangle size={56} className="mx-auto text-slate-600 mb-4" />
                <p className="text-slate-300 text-lg font-semibold">Select a roster to view conflicts</p>
              </div>
            ) : totalConflicts === 0 ? (
              <div className="py-24 text-center">
                <CheckCircle size={56} className="mx-auto text-green-400 mb-4" />
                <p className="text-slate-200 text-lg font-bold">No conflicts found</p>
                <p className="text-slate-400 text-base mt-2">All constraints are satisfied! 🎉</p>
              </div>
            ) : (
              <>
                <div className="space-y-4 mb-8">
                  {paginatedConflicts.map((conflict: any, index: number) => (
                    <div
                      key={conflict.id}
                      onMouseEnter={() => setHoveredConflict(conflict.id)}
                      onMouseLeave={() => setHoveredConflict(null)}
                      className={`p-6 rounded-2xl border backdrop-blur transition-all ${
                        conflict.resolved || resolvedConflicts.has(conflict.id)
                          ? 'bg-gradient-to-r from-green-900/20 to-emerald-900/20 border-green-700/40 hover:border-green-600/60'
                          : error?.conflictId === conflict.id
                          ? 'bg-gradient-to-r from-red-900/30 to-orange-900/30 border-red-700/50 hover:border-red-600/70'
                          : severityConfig[conflict.severity]?.bgColor || 'bg-slate-700/30 border-slate-600/30 hover:border-slate-500/60'
                      } ${hoveredConflict === conflict.id ? 'shadow-xl' : 'shadow-lg'} group/conflict`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          {/* Error Alert */}
                          {error?.conflictId === conflict.id && (
                            <div className="mb-4 p-4 bg-gradient-to-r from-red-900/40 to-orange-900/40 rounded-xl border border-red-700/50 flex items-start gap-3">
                              <AlertTriangle size={20} className="text-red-300 flex-shrink-0 mt-1" />
                              <div>
                                <p className="text-sm font-bold text-red-200">Resolution Failed</p>
                                <p className="text-xs text-red-300 mt-1">{error.message}</p>
                              </div>
                              <button
                                onClick={() => setError(null)}
                                className="ml-auto text-red-300 hover:text-red-200 transition-colors"
                              >
                                ✕
                              </button>
                            </div>
                          )}

                          {/* Header with index and badges */}
                          <div className="flex items-center gap-3 mb-4 flex-wrap">
                            <span className="text-sm font-bold text-white bg-gradient-to-r from-slate-700 to-slate-600 px-4 py-2 rounded-lg border border-slate-500/30 shadow-lg">
                              #{startIdx + index + 1}
                            </span>
                            <span
                              className={`px-4 py-2 rounded-lg text-xs font-bold ${
                                severityConfig[conflict.severity]?.color || 'text-slate-300'
                              }`}
                            >
                              {severityConfig[conflict.severity]?.icon} {conflict.severity.toUpperCase()}
                            </span>
                            {(conflict.resolved || resolvedConflicts.has(conflict.id)) && (
                              <span className="px-4 py-2 rounded-lg text-xs font-bold bg-gradient-to-r from-green-900/60 to-emerald-900/60 text-green-300 border border-green-700/50 flex items-center gap-2 shadow-lg">
                                <CheckCircle size={14} />
                                ✓ RESOLVED
                              </span>
                            )}
                            <span className="text-xs text-slate-400 font-mono bg-slate-700/30 px-3 py-1 rounded-lg">{conflict.conflict_type}</span>
                          </div>

                          {/* Description */}
                          <p className="text-white font-bold text-base mb-4 group-hover/conflict:text-blue-200 transition-colors">{conflict.description}</p>

                          {/* Details */}
                          <div className="grid grid-cols-3 gap-4 text-sm text-slate-400 mb-4">
                            <div className="flex items-center gap-2">
                              <span className="text-base">📅</span>
                              <span className="font-mono text-xs bg-slate-700/40 px-3 py-1 rounded">{conflict.conflict_date}</span>
                            </div>
                            {conflict.employee_id && (
                              <div className="flex items-center gap-2">
                                <span className="text-base">👤</span>
                                <span className="font-mono text-xs bg-slate-700/40 px-3 py-1 rounded">{conflict.employee_id.slice(0, 8)}...</span>
                              </div>
                            )}
                            {conflict.brand_id && (
                              <div className="flex items-center gap-2">
                                <span className="text-base">🏢</span>
                                <span className="font-mono text-xs bg-slate-700/40 px-3 py-1 rounded">{conflict.brand_id.slice(0, 8)}...</span>
                              </div>
                            )}
                          </div>

                          {/* Suggested Resolution */}
                          {conflict.suggested_resolution && (
                            <div className="p-4 bg-gradient-to-r from-blue-900/30 to-cyan-900/30 rounded-xl border border-blue-700/40 mt-4">
                              <p className="text-xs font-bold text-blue-300 mb-2 uppercase tracking-wide">💡 Suggested Resolution:</p>
                              <p className="text-sm text-blue-200">{conflict.suggested_resolution}</p>
                            </div>
                          )}
                        </div>

                        {/* Action Button */}
                        <div className="ml-6 flex-shrink-0">
                          {conflict.resolved || resolvedConflicts.has(conflict.id) ? (
                            <div className="flex items-center gap-2 text-green-400 bg-gradient-to-r from-green-900/40 to-emerald-900/40 px-5 py-3 rounded-xl border border-green-700/50 shadow-lg">
                              <CheckCircle size={18} />
                              <span className="text-sm font-bold">Resolved</span>
                            </div>
                          ) : (
                            <button
                              onClick={() => handleResolve(conflict.id)}
                              disabled={resolveMutation.isPending}
                              className="px-6 py-3 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:from-blue-700 hover:via-blue-600 hover:to-cyan-600 text-white text-sm rounded-xl font-bold disabled:opacity-50 transition-all transform hover:scale-105 active:scale-95 shadow-lg hover:shadow-xl flex items-center gap-2 min-w-max"
                            >
                              {resolveMutation.isPending ? (
                                <>
                                  <Loader size={16} className="animate-spin" />
                                  Resolving...
                                </>
                              ) : (
                                <>
                                  <CheckCircle size={16} />
                                  Resolve
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Premium Pagination Controls */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-6 pt-10 border-t border-slate-700/30">
                    <button
                      onClick={() => setConflictsPage(Math.max(1, conflictsPage - 1))}
                      disabled={conflictsPage === 1}
                      className="p-3 rounded-xl bg-slate-700/40 hover:bg-slate-700/60 disabled:opacity-30 disabled:cursor-not-allowed text-slate-300 hover:text-white transition-all transform hover:scale-110 border border-slate-600/30"
                    >
                      <ChevronLeft size={22} />
                    </button>

                    <div className="flex gap-3">
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        let page;
                        if (totalPages <= 5) {
                          page = i + 1;
                        } else if (conflictsPage <= 3) {
                          page = i + 1;
                        } else if (conflictsPage >= totalPages - 2) {
                          page = totalPages - 4 + i;
                        } else {
                          page = conflictsPage - 2 + i;
                        }
                        return (
                          <button
                            key={page}
                            onClick={() => setConflictsPage(page)}
                            className={`w-12 h-12 rounded-xl font-bold transition-all transform hover:scale-110 ${
                              conflictsPage === page
                                ? 'bg-gradient-to-r from-red-600 to-pink-600 text-white shadow-lg shadow-red-500/50'
                                : 'bg-slate-700/40 text-slate-300 hover:bg-slate-700/60 border border-slate-600/30'
                            }`}
                          >
                            {page}
                          </button>
                        );
                      })}
                    </div>

                    <button
                      onClick={() => setConflictsPage(Math.min(totalPages, conflictsPage + 1))}
                      disabled={conflictsPage === totalPages}
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
      </div>
    </div>
  )
}
