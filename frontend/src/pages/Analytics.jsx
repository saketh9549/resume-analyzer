import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { getDashboardStats, getAnalyticsHistory, listResumes, getParsedResume } from "../services/api"
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar 
} from "recharts"
import { 
  BarChart3, 
  TrendingUp, 
  Cpu, 
  Award, 
  Layers, 
  RefreshCw, 
  Briefcase, 
  Sparkles 
} from "lucide-react"

export default function Analytics() {
  const [stats, setStats] = useState({ avg_score: "0%", skills_found: "0", job_matches: "0", total_uploads: "0" })
  const [history, setHistory] = useState([])
  const [resumes, setResumes] = useState([])
  const [recentAtsBreakdown, setRecentAtsBreakdown] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadData() {
      try {
        const dashboardStats = await getDashboardStats()
        setStats(dashboardStats)

        const hist = await getAnalyticsHistory()
        setHistory(hist)

        const list = await listResumes()
        setResumes(list)

        // Fetch most recent resume's detailed 10-dimensional ATS breakdown if available
        if (list && list.length > 0) {
          const recentId = list[0].id
          const parsed = await getParsedResume(recentId)
          if (parsed && parsed.ats_breakdown && parsed.ats_breakdown.length > 0) {
            setRecentAtsBreakdown(parsed.ats_breakdown)
          }
        }
      } catch (err) {
        console.error("Failed to load analytics details:", err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  // Calculate radar data from recent resumes category scores if available,
  // or fall back to high-grade standard mock data for preview
  const radarData = recentAtsBreakdown.length > 0
    ? recentAtsBreakdown.map(item => ({
        subject: item.title,
        A: item.score,
        B: 75, // Benchmark average target
        fullMark: 100
      }))
    : [
        { subject: "Impact", A: 85, B: 110, fullMark: 150 },
        { subject: "Skills", A: 98, B: 130, fullMark: 150 },
        { subject: "Experience", A: 86, B: 130, fullMark: 150 },
        { subject: "Formatting", A: 90, B: 100, fullMark: 150 },
        { subject: "Education", A: 70, B: 90, fullMark: 150 },
        { subject: "Projects", A: 82, B: 100, fullMark: 150 },
      ]

  return (
    <div className="space-y-8 pb-12">
      {/* Title */}
      <div>
        <h1 className="text-5xl font-black bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent tracking-tight">
          Personal Career Intelligence
        </h1>
        <p className="text-gray-400 mt-2 text-sm font-medium">
          Multidimensional analytics covering ATS scores progression, skills inventories, and visual formatting benchmarks.
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-32">
          <RefreshCw className="animate-spin text-blue-400" size={36} />
        </div>
      ) : (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl flex items-center gap-4 hover:border-blue-500/20 transition-colors">
              <div className="p-3 bg-blue-500/10 text-blue-400 rounded-2xl">
                <Layers size={22} />
              </div>
              <div>
                <span className="block text-[10px] text-gray-500 font-bold uppercase tracking-wider">Total Resumes</span>
                <span className="text-2xl font-black text-gray-200 mt-0.5 block">{stats.total_uploads}</span>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl flex items-center gap-4 hover:border-green-500/20 transition-colors">
              <div className="p-3 bg-green-500/10 text-green-400 rounded-2xl">
                <Award size={22} />
              </div>
              <div>
                <span className="block text-[10px] text-gray-500 font-bold uppercase tracking-wider">Avg ATS Rating</span>
                <span className="text-2xl font-black text-gray-200 mt-0.5 block">{stats.avg_score}</span>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl flex items-center gap-4 hover:border-purple-500/20 transition-colors">
              <div className="p-3 bg-purple-500/10 text-purple-400 rounded-2xl">
                <Cpu size={22} />
              </div>
              <div>
                <span className="block text-[10px] text-gray-500 font-bold uppercase tracking-wider">Indexed Skills</span>
                <span className="text-2xl font-black text-gray-200 mt-0.5 block">{stats.skills_found}</span>
              </div>
            </div>

            <div className="bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl flex items-center gap-4 hover:border-yellow-500/20 transition-colors">
              <div className="p-3 bg-yellow-500/10 text-yellow-400 rounded-2xl">
                <Briefcase size={22} />
              </div>
              <div>
                <span className="block text-[10px] text-gray-500 font-bold uppercase tracking-wider">Target Matches</span>
                <span className="text-2xl font-black text-gray-200 mt-0.5 block">{stats.job_matches}</span>
              </div>
            </div>
          </div>

          {/* Core Analytics Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Trajectory Timeline Chart */}
            <div className="lg:col-span-7 bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl space-y-6">
              <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2 border-b border-white/5 pb-3">
                <TrendingUp size={18} className="text-blue-400" /> ATS Compatibility Trajectory
              </h3>
              <div className="h-[280px] w-full text-xs font-semibold">
                {history.length > 0 && history[0].name !== "No Data" ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={history}>
                      <defs>
                        <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.4}/>
                          <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="name" stroke="#64748B" fontSize={9} tickLine={false} />
                      <YAxis stroke="#64748B" domain={[0, 100]} fontSize={9} tickLine={false} axisLine={false} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: "#0F172A", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "12px" }}
                        labelStyle={{ color: "#F3F4F6", fontWeight: "bold" }}
                      />
                      <Area type="monotone" dataKey="score" stroke="#3B82F6" strokeWidth={2.5} fillOpacity={1} fill="url(#colorScore)" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-gray-500 italic space-y-2">
                    <TrendingUp size={36} className="text-gray-600 animate-pulse" />
                    <span>Upload multiple resume versions to view scoring history trends over time.</span>
                  </div>
                )}
              </div>
            </div>

            {/* Radar Section Capability */}
            <div className="lg:col-span-5 bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl space-y-6">
              <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2 border-b border-white/5 pb-3">
                <BarChart3 size={18} className="text-purple-400" /> Dimension Capability Mapping
              </h3>
              <div className="h-[250px] w-full flex items-center justify-center text-[10px] font-bold">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.05)" />
                    <PolarAngleAxis dataKey="subject" stroke="#64748B" fontSize={9} />
                    <PolarRadiusAxis angle={30} domain={[0, recentAtsBreakdown.length > 0 ? 100 : 150]} stroke="#64748B" fontSize={8} />
                    <Radar name="Target Profile" dataKey="A" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.25} />
                    <Radar name="Benchmark Average" dataKey="B" stroke="#A855F7" fill="#A855F7" fillOpacity={0.1} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: "#0F172A", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "12px" }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>

          {/* Historical Resume Submissions table */}
          <div className="bg-slate-900/60 p-6 md:p-8 rounded-3xl border border-white/5 backdrop-blur-xl space-y-6">
            <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2 border-b border-white/5 pb-4">
              <Sparkles size={18} className="text-yellow-400" /> Version Index Logs
            </h3>
            {resumes.length === 0 ? (
              <p className="text-xs text-gray-500 italic text-center py-6">No historical records in pipeline logs.</p>
            ) : (
              <div className="overflow-x-auto w-full">
                <table className="w-full text-left text-xs font-semibold text-gray-300 border-collapse">
                  <thead>
                    <tr className="border-b border-white/5 text-[10px] text-gray-500 uppercase tracking-wider font-bold">
                      <th className="py-3 px-4">Resume Version Filename</th>
                      <th className="py-3 px-4">ATS Overall Rating</th>
                      <th className="py-3 px-4">Identified Category</th>
                      <th className="py-3 px-4">Index Timestamp</th>
                      <th className="py-3 px-4">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {resumes.map((r) => (
                      <tr key={r.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                        <td className="py-3.5 px-4 font-bold text-gray-200">{r.name}</td>
                        <td className="py-3.5 px-4">
                          <span className={`font-black ${
                            parseInt(r.score) >= 80 
                              ? "text-emerald-400" 
                              : parseInt(r.score) >= 60 
                              ? "text-yellow-400" 
                              : "text-rose-400"
                          }`}>
                            {r.score}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-gray-400">{r.category}</td>
                        <td className="py-3.5 px-4 text-gray-500 font-medium">{r.date}</td>
                        <td className="py-3.5 px-4">
                          <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[9px] font-bold border border-emerald-500/10">
                            {r.analysis_status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}