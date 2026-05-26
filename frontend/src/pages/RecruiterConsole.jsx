import { useState, useEffect } from "react"
import { searchCandidates, addCandidateToShortlist, getRecruiterShortlist, getRecruiterAnalytics } from "../services/api"
import { motion } from "framer-motion"
import { Search, UserCheck, BarChart3, Users, Award, ShieldAlert, Sparkles, RefreshCw, PlusCircle, CheckCircle } from "lucide-react"

function RecruiterConsole() {
  const [candidates, setCandidates] = useState([])
  const [shortlist, setShortlist] = useState({ candidates: [] })
  const [analytics, setAnalytics] = useState({ total_candidates: 0, avg_ats: "0%", top_skills: [] })
  const [loading, setLoading] = useState(true)
  
  // Search parameters
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState("candidates") // candidates | shortlist

  // UI state feedback
  const [shortlistedMap, setShortlistedMap] = useState({})

  useEffect(() => {
    async function loadInitialData() {
      try {
        const list = await searchCandidates("")
        setCandidates(list)

        const sl = await getRecruiterShortlist()
        setShortlist(sl)
        
        // Map shortlisted candidates for immediate UI indicator feedback
        const mapped = {}
        sl.candidates.forEach(c => {
          mapped[c.resume_id] = true
        })
        setShortlistedMap(mapped)

        const stats = await getRecruiterAnalytics()
        setAnalytics(stats)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    loadInitialData()
  }, [])

  const handleSearchSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await searchCandidates(searchQuery)
      setCandidates(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleAddShortlist = async (candidateId, notes = "Recruiter pipeline shortlist") => {
    try {
      const res = await addCandidateToShortlist(candidateId, notes)
      if (res && !res.error) {
        setShortlistedMap(prev => ({ ...prev, [candidateId]: true }))
        // Refresh shortlist display
        const sl = await getRecruiterShortlist()
        setShortlist(sl)
      }
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Title */}
      <div>
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          Recruiter Talent Console
        </h1>
        <p className="text-gray-400 mt-2 text-lg">
          Query candidate profiles semantically, inspect ATS compatibility, and manage hiring shortlists.
        </p>
      </div>

      {/* Recruiter Dashboard Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-400 border border-blue-500/10 rounded-2xl">
            <Users size={24} />
          </div>
          <div>
            <span className="block text-xs text-gray-400 font-semibold uppercase">Total Candidates</span>
            <span className="text-2xl font-black text-gray-200">{analytics.total_candidates}</span>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md flex items-center gap-4">
          <div className="p-3 bg-green-500/10 text-green-400 border border-green-500/10 rounded-2xl">
            <Award size={24} />
          </div>
          <div>
            <span className="block text-xs text-gray-400 font-semibold uppercase">Average ATS Score</span>
            <span className="text-2xl font-black text-gray-200">{analytics.avg_ats}</span>
          </div>
        </div>

        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md flex items-center gap-4">
          <div className="p-3 bg-purple-500/10 text-purple-400 border border-purple-500/10 rounded-2xl">
            <BarChart3 size={24} />
          </div>
          <div className="flex-1 min-w-0">
            <span className="block text-xs text-gray-400 font-semibold uppercase mb-1">Top Skill Density</span>
            <div className="flex flex-wrap gap-1.5">
              {analytics.top_skills?.slice(0, 3).map(s => (
                <span key={s.skill} className="px-2 py-0.5 rounded bg-white/5 border border-white/5 text-[9px] text-gray-300 font-bold">
                  {s.skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation tabs */}
      <div className="flex border-b border-white/10 gap-6">
        <button
          onClick={() => setActiveTab("candidates")}
          className={`pb-3 font-semibold text-sm transition-all border-b-2 ${
            activeTab === "candidates" ? "border-blue-500 text-blue-400 font-bold" : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          Candidate Directory
        </button>
        <button
          onClick={() => setActiveTab("shortlist")}
          className={`pb-3 font-semibold text-sm transition-all border-b-2 ${
            activeTab === "shortlist" ? "border-blue-500 text-blue-400 font-bold" : "border-transparent text-gray-400 hover:text-gray-200"
          }`}
        >
          Shortlisted Pipeline ({shortlist.candidates?.length || 0})
        </button>
      </div>

      {/* SEARCH BAR (Only for candidates directory) */}
      {activeTab === "candidates" && (
        <div className="bg-white/5 border border-white/10 p-5 rounded-3xl backdrop-blur-md">
          <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-4 items-center">
            <div className="flex-1 w-full flex items-center gap-3 bg-slate-900 border border-white/10 px-5 py-3.5 rounded-2xl focus-within:border-blue-500 transition">
              <Search size={18} className="text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search candidates semantically (e.g. Frontend developer experienced in NextJS, or Docker expert)..."
                className="flex-1 bg-transparent text-gray-200 outline-none text-sm placeholder-gray-500"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto px-6 py-3.5 bg-blue-500 hover:bg-blue-600 transition font-semibold rounded-2xl text-white cursor-pointer shadow-lg shadow-blue-500/20 shrink-0"
            >
              Run Semantic Search
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-24">
          <RefreshCw className="animate-spin text-blue-400" size={32} />
        </div>
      ) : activeTab === "candidates" && candidates.length === 0 ? (
        <div className="bg-white/5 border border-white/10 p-16 rounded-3xl text-center space-y-4 max-w-xl mx-auto backdrop-blur-md">
          <ShieldAlert size={40} className="mx-auto text-blue-400" />
          <h3 className="text-xl font-bold text-gray-200">No Candidates Found</h3>
          <p className="text-gray-400 text-sm">
            Please parse candidate resumes onto the platform first.
          </p>
        </div>
      ) : activeTab === "candidates" ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fadeIn">
          {candidates.map((cand) => (
            <div
              key={cand.id}
              className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md flex flex-col justify-between hover:border-blue-500/30 transition duration-300 group"
            >
              <div className="space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-gray-200 text-base leading-snug group-hover:text-blue-400 transition">
                      {cand.filename}
                    </h4>
                    <span className="text-xs text-gray-400 block mt-1">{cand.user_email}</span>
                  </div>

                  {/* Similarity check */}
                  {cand.similarity_score !== undefined ? (
                    <span className="shrink-0 px-2.5 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/10 rounded-xl text-[10px] font-black">
                      {cand.similarity_score}% Match
                    </span>
                  ) : (
                    <span className="shrink-0 px-2.5 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/10 rounded-xl text-[10px] font-black">
                      ATS: {cand.ats_score}%
                    </span>
                  )}
                </div>

                {/* Technical skills list */}
                <div className="flex flex-wrap gap-1.5 pt-2">
                  {cand.skills?.slice(0, 7).map(s => (
                    <span key={s} className="px-2 py-0.5 rounded bg-white/5 border border-white/5 text-[10px] text-gray-400 font-semibold">
                      {s}
                    </span>
                  ))}
                  {cand.skills?.length > 7 && (
                    <span className="text-[10px] text-gray-500 self-center">+{cand.skills.length - 7} more</span>
                  )}
                </div>
              </div>

              <div className="pt-6">
                {shortlistedMap[cand.id] ? (
                  <div className="w-full flex items-center justify-center gap-1.5 px-4 py-2.5 bg-green-500/10 text-green-400 border border-green-500/15 rounded-xl font-bold text-xs">
                    <CheckCircle size={12} /> Candidate Shortlisted
                  </div>
                ) : (
                  <button
                    onClick={() => handleAddShortlist(cand.id)}
                    className="w-full flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-blue-500/10 hover:bg-blue-500 text-blue-400 hover:text-white border border-blue-500/20 group-hover:border-blue-500/50 transition-all font-bold text-xs cursor-pointer"
                  >
                    <PlusCircle size={13} /> Add to Hiring Shortlist
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : shortlist.candidates.length === 0 ? (
        <div className="bg-white/5 border border-white/10 p-16 rounded-3xl text-center text-gray-400 text-sm max-w-xl mx-auto backdrop-blur-md">
          <UserCheck size={40} className="mx-auto text-gray-500 mb-4" />
          No candidates have been shortlisted in your pipeline yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fadeIn">
          {shortlist.candidates.map((cand) => (
            <div
              key={cand.resume_id}
              className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md flex flex-col justify-between border-green-500/20"
            >
              <div className="space-y-4">
                <div>
                  <h4 className="font-bold text-gray-200 text-base leading-snug">
                    {cand.filename}
                  </h4>
                  <span className="text-xs text-gray-400 block mt-1">{cand.user_email}</span>
                </div>
                
                <div className="p-3.5 bg-slate-900 border border-white/5 rounded-2xl text-xs text-gray-400 leading-relaxed font-semibold">
                  <strong>Notes: </strong>{cand.notes}
                </div>
                
                <div className="text-[10px] text-gray-500 font-medium">Added to pipeline: {cand.added_at.slice(0, 10)}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default RecruiterConsole
