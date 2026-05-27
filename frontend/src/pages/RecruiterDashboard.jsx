import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { getRecruiterAnalytics, getRecruiterShortlist, getRecruiterJobs } from "../services/api"
import { 
  Users, 
  Award, 
  Briefcase, 
  UserCheck, 
  Search, 
  PlusCircle, 
  BarChart3, 
  ArrowRight,
  TrendingUp
} from "lucide-react"
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell 
} from "recharts"

export default function RecruiterDashboard({ onViewChange }) {
  const [analytics, setAnalytics] = useState({ total_candidates: 0, avg_ats: "0%", top_skills: [] })
  const [shortlistCount, setShortlistCount] = useState(0)
  const [jobsCount, setJobsCount] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadStats() {
      try {
        const stats = await getRecruiterAnalytics()
        setAnalytics(stats)

        const sl = await getRecruiterShortlist()
        setShortlistCount(sl.candidates?.length || 0)

        const jobs = await getRecruiterJobs()
        setJobsCount(jobs.length || 0)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    loadStats()
  }, [])

  const skillData = analytics.top_skills?.map(s => ({
    name: s.skill,
    count: s.count
  })) || []

  // Mock ATS Band Distribution Chart
  const atsDistribution = [
    { name: "80-100% (High)", value: 5, color: "#10B981" },
    { name: "60-80% (Mid)", value: 8, color: "#F59E0B" },
    { name: "Below 60% (Low)", value: 3, color: "#EF4444" },
  ]

  return (
    <div className="space-y-8 pb-12">
      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl flex items-center gap-4 hover:border-blue-500/20 transition-colors">
          <div className="p-3 bg-blue-500/10 text-blue-400 border border-blue-500/10 rounded-2xl">
            <Users size={24} />
          </div>
          <div>
            <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider">Total Candidates</span>
            <span className="text-2xl font-black text-gray-200 mt-0.5 block">{analytics.total_candidates}</span>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl flex items-center gap-4 hover:border-green-500/20 transition-colors">
          <div className="p-3 bg-green-500/10 text-green-400 border border-green-500/10 rounded-2xl">
            <Award size={24} />
          </div>
          <div>
            <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider">Average ATS Score</span>
            <span className="text-2xl font-black text-gray-200 mt-0.5 block">{analytics.avg_ats}</span>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl flex items-center gap-4 hover:border-purple-500/20 transition-colors">
          <div className="p-3 bg-purple-500/10 text-purple-400 border border-purple-500/10 rounded-2xl">
            <Briefcase size={24} />
          </div>
          <div>
            <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider">Jobs Indexed</span>
            <span className="text-2xl font-black text-gray-200 mt-0.5 block">{jobsCount}</span>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl flex items-center gap-4 hover:border-yellow-500/20 transition-colors">
          <div className="p-3 bg-yellow-500/10 text-yellow-400 border border-yellow-500/10 rounded-2xl">
            <UserCheck size={24} />
          </div>
          <div>
            <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider">Shortlist Count</span>
            <span className="text-2xl font-black text-gray-200 mt-0.5 block">{shortlistCount}</span>
          </div>
        </div>
      </div>

      {/* Visual Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Skills Density */}
        <div className="lg:col-span-7 bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl space-y-6">
          <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2 border-b border-white/5 pb-3">
            <TrendingUp size={18} className="text-blue-400" /> Talent Pool Skill Density
          </h3>
          <div className="h-[250px] w-full text-xs">
            {skillData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={skillData}>
                  <XAxis dataKey="name" stroke="#64748B" fontSize={10} tickLine={false} />
                  <YAxis stroke="#64748B" fontSize={10} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#0F172A", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "12px" }}
                    labelStyle={{ color: "#F3F4F6", fontWeight: "bold" }}
                  />
                  <Bar dataKey="count" fill="url(#colorSkill)" radius={[6, 6, 0, 0]}>
                    {skillData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index % 2 === 0 ? "#3B82F6" : "#A855F7"} />
                    ))}
                  </Bar>
                  <defs>
                    <linearGradient id="colorSkill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#A855F7" stopOpacity={0.8}/>
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500 italic">
                No skill telemetry available yet. Parse resumes to populate analytics.
              </div>
            )}
          </div>
        </div>

        {/* ATS Score Bands */}
        <div className="lg:col-span-5 bg-slate-900/60 border border-white/5 p-6 rounded-3xl backdrop-blur-xl space-y-6">
          <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2 border-b border-white/5 pb-3">
            <BarChart3 size={18} className="text-purple-400" /> Candidate Matching Quality
          </h3>
          <div className="h-[200px] w-full flex items-center justify-center">
            {analytics.total_candidates > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={atsDistribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={75}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {atsDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#0F172A", border: "1px solid rgba(255,255,255,0.1)", borderRadius: "12px" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-gray-500 italic text-xs">No matching distributions.</div>
            )}
          </div>
          <div className="flex justify-around text-[10px] font-bold text-gray-400">
            {atsDistribution.map((d) => (
              <span key={d.name} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full block" style={{ backgroundColor: d.color }} />
                {d.name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Recruiter Console Quick Links */}
      <div className="bg-slate-900/60 p-8 rounded-3xl border border-white/5 backdrop-blur-xl space-y-6">
        <h3 className="text-xl font-black text-gray-100 tracking-tight">Recruiter Operations Hub</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <div 
            onClick={() => onViewChange("candidates")}
            className="bg-slate-950/40 p-5 rounded-2xl border border-white/5 hover:border-blue-500/30 transition duration-300 group cursor-pointer space-y-4"
          >
            <div className="p-3 bg-blue-500/10 text-blue-400 rounded-xl w-fit">
              <Search size={20} />
            </div>
            <div>
              <h4 className="font-bold text-sm text-gray-200 flex items-center gap-1 group-hover:text-blue-400 transition">
                Candidate Directory <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </h4>
              <p className="text-[11px] text-gray-400 leading-relaxed mt-1">
                Query profiles semantically and filter by skills or specific ATS rating levels.
              </p>
            </div>
          </div>

          <div 
            onClick={() => onViewChange("jobs")}
            className="bg-slate-950/40 p-5 rounded-2xl border border-white/5 hover:border-purple-500/30 transition duration-300 group cursor-pointer space-y-4"
          >
            <div className="p-3 bg-purple-500/10 text-purple-400 rounded-xl w-fit">
              <PlusCircle size={20} />
            </div>
            <div>
              <h4 className="font-bold text-sm text-gray-200 flex items-center gap-1 group-hover:text-purple-400 transition">
                Manage Job Postings <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </h4>
              <p className="text-[11px] text-gray-400 leading-relaxed mt-1">
                Post new JDs to index them semantically for candidate matches.
              </p>
            </div>
          </div>

          <div 
            onClick={() => onViewChange("shortlist")}
            className="bg-slate-950/40 p-5 rounded-2xl border border-white/5 hover:border-yellow-500/30 transition duration-300 group cursor-pointer space-y-4"
          >
            <div className="p-3 bg-yellow-500/10 text-yellow-400 rounded-xl w-fit">
              <UserCheck size={20} />
            </div>
            <div>
              <h4 className="font-bold text-sm text-gray-200 flex items-center gap-1 group-hover:text-yellow-400 transition">
                Shortlisted Pipeline <ArrowRight size={14} className="group-hover:translate-x-1 transition-transform" />
              </h4>
              <p className="text-[11px] text-gray-400 leading-relaxed mt-1">
                Review candidate pipelines and notes shortlist assignments.
              </p>
            </div>
          </div>

        </div>
      </div>
    </div>
  )
}
