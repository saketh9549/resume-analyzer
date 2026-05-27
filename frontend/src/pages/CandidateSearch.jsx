import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { searchCandidates, addCandidateToShortlist, getRecruiterShortlist } from "../services/api"
import { Search, UserCheck, Plus, Check, Loader2, Sparkles, Filter, Award, Eye } from "lucide-react"
import { useToast } from "../context/ToastContext"

export default function CandidateSearch({ onInspectCandidate }) {
  const { showToast } = useToast()
  const [candidates, setCandidates] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [shortlistedMap, setShortlistedMap] = useState({})
  const [shortlistNotes, setShortlistNotes] = useState("")
  const [activeNotesCandId, setActiveNotesCandId] = useState(null)

  // Filters
  const [atsThreshold, setAtsThreshold] = useState(0)

  const loadData = async (query = "") => {
    setLoading(true)
    try {
      const data = await searchCandidates(query)
      setCandidates(data)

      const sl = await getRecruiterShortlist()
      const mapped = {}
      sl.candidates.forEach(c => {
        mapped[c.resume_id] = true
      })
      setShortlistedMap(mapped)
    } catch (err) {
      showToast("Failed to load candidate information.", "error")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleSearch = (e) => {
    e.preventDefault()
    loadData(searchQuery)
  }

  const handleShortlist = async (candidateId) => {
    try {
      const res = await addCandidateToShortlist(candidateId, shortlistNotes || "Added to pipeline shortlist")
      if (res.error) {
        showToast(res.error, "error")
      } else {
        showToast("Candidate successfully shortlisted!", "success")
        setShortlistedMap(prev => ({ ...prev, [candidateId]: true }))
        setActiveNotesCandId(null)
        setShortlistNotes("")
      }
    } catch (err) {
      showToast("Shortlist update failed.", "error")
    }
  }

  const filteredCandidates = candidates.filter(c => c.ats_score >= atsThreshold)

  return (
    <div className="space-y-6">
      {/* Search Header panel */}
      <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 backdrop-blur-xl space-y-4">
        <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4 items-center">
          <div className="flex-1 w-full flex items-center gap-3 bg-slate-950/60 border border-white/10 px-5 py-3.5 rounded-2xl focus-within:border-blue-500 transition">
            <Search size={18} className="text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search candidate skills & experience semantically (e.g. Node developer with AWS Docker setup, or Python stats engineer)..."
              className="flex-1 bg-transparent text-gray-200 outline-none text-xs placeholder-gray-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 transition font-bold rounded-xl text-white cursor-pointer shadow-lg shadow-blue-500/20 shrink-0 text-xs"
          >
            {loading ? (
              <span className="flex items-center gap-1.5 justify-center">
                <Loader2 size={14} className="animate-spin" /> Querying...
              </span>
            ) : (
              <span className="flex items-center gap-1.5 justify-center">
                <Sparkles size={14} /> Semantic Match
              </span>
            )}
          </button>
        </form>

        {/* Filter Toolbar */}
        <div className="flex flex-wrap items-center gap-4 text-xs pt-2 border-t border-white/5 text-gray-400 font-semibold">
          <div className="flex items-center gap-1.5">
            <Filter size={13} className="text-gray-500" />
            <span>ATS Filter:</span>
          </div>
          <div className="flex gap-2">
            {[0, 50, 70, 80].map((t) => (
              <button
                key={t}
                onClick={() => setAtsThreshold(t)}
                className={`px-3 py-1 rounded-lg border transition ${
                  atsThreshold === t
                    ? "bg-blue-500/10 border-blue-500/25 text-blue-400 font-bold"
                    : "bg-white/5 border-white/5 hover:bg-white/10"
                }`}
              >
                {t === 0 ? "All Scores" : `>= ${t}%`}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Directory Grid */}
      {loading ? (
        <div className="flex justify-center items-center py-24">
          <Loader2 className="animate-spin text-blue-400" size={36} />
        </div>
      ) : filteredCandidates.length === 0 ? (
        <div className="bg-slate-900/40 p-20 rounded-3xl text-center space-y-4 border border-white/5">
          <Award size={48} className="mx-auto text-gray-600" />
          <h4 className="text-lg font-bold text-gray-300">No Match Criteria Met</h4>
          <p className="text-xs text-gray-500 max-w-sm mx-auto">
            Try adjusting search queries or resetting the ATS filters to expand candidate search bands.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredCandidates.map((cand) => (
            <motion.div
              key={cand.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-slate-900/60 border border-white/5 hover:border-white/10 p-6 rounded-3xl backdrop-blur-xl flex flex-col justify-between hover:scale-[1.01] transition-all duration-300 group"
            >
              <div className="space-y-4">
                <div className="flex justify-between items-start">
                  <div className="min-w-0 flex-1 pr-4">
                    <h4 className="font-bold text-gray-100 text-base leading-snug group-hover:text-blue-400 transition truncate">
                      {cand.filename}
                    </h4>
                    <span className="text-xs text-gray-400 block mt-1 truncate">{cand.user_email}</span>
                  </div>

                  {/* Matching score display */}
                  {cand.similarity_score !== undefined ? (
                    <div className="flex flex-col items-end shrink-0">
                      <span className="px-2.5 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/10 rounded-xl text-[10px] font-black">
                        {cand.similarity_score}% Match
                      </span>
                      <span className="text-[9px] text-gray-500 mt-1 font-bold">ATS: {cand.ats_score}%</span>
                    </div>
                  ) : (
                    <span className="shrink-0 px-2.5 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/10 rounded-xl text-[10px] font-black">
                      ATS: {cand.ats_score}%
                    </span>
                  )}
                </div>

                {/* Candidate technical skills */}
                {cand.skills?.length > 0 ? (
                  <div className="flex flex-wrap gap-1.5 pt-2">
                    {cand.skills.slice(0, 8).map(s => (
                      <span key={s} className="px-2 py-0.5 rounded bg-white/5 border border-white/5 text-[9px] text-gray-400 font-semibold">
                        {s}
                      </span>
                    ))}
                    {cand.skills.length > 8 && (
                      <span className="text-[9px] text-gray-500 self-center">+{cand.skills.length - 8} more</span>
                    )}
                  </div>
                ) : (
                  <p className="text-xs text-gray-500 italic">No skills cataloged.</p>
                )}
              </div>

              {/* Inspect / Shortlist Actions */}
              <div className="pt-6 space-y-3">
                {activeNotesCandId === cand.id ? (
                  <div className="space-y-2 animate-fadeIn">
                    <input
                      type="text"
                      value={shortlistNotes}
                      onChange={(e) => setShortlistNotes(e.target.value)}
                      placeholder="Add hiring pipeline notes (e.g. Schedule call)..."
                      className="w-full bg-slate-950 border border-white/10 px-3 py-2 rounded-xl text-xs text-gray-200 outline-none focus:border-blue-500"
                    />
                    <div className="flex gap-2 text-[10px] font-bold">
                      <button
                        onClick={() => handleShortlist(cand.id)}
                        className="flex-1 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white transition font-bold cursor-pointer"
                      >
                        Confirm Shortlist
                      </button>
                      <button
                        onClick={() => {
                          setActiveNotesCandId(null)
                          setShortlistNotes("")
                        }}
                        className="px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-gray-400 transition"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() => onInspectCandidate(cand.id)}
                      className="flex-1 flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/5 hover:border-white/10 text-gray-300 transition-all font-bold text-xs cursor-pointer"
                    >
                      <Eye size={13} /> View Full Profile
                    </button>

                    {shortlistedMap[cand.id] ? (
                      <div className="px-4 py-2.5 bg-green-500/10 text-green-400 border border-green-500/15 rounded-xl font-bold text-xs flex items-center gap-1">
                        <Check size={12} /> Shortlisted
                      </div>
                    ) : (
                      <button
                        onClick={() => {
                          setActiveNotesCandId(cand.id)
                          setShortlistNotes("")
                        }}
                        className="flex items-center gap-1 px-4 py-2.5 rounded-xl bg-blue-500/15 hover:bg-blue-500 text-blue-400 hover:text-white border border-blue-500/20 transition-all font-bold text-xs cursor-pointer"
                      >
                        <Plus size={13} /> Shortlist
                      </button>
                    )}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
