import React, { useState, useEffect } from "react"
import { getRecruiterShortlist } from "../services/api"
import { motion } from "framer-motion"
import { 
  UserCheck, 
  ShieldAlert, 
  Sparkles, 
  RefreshCw, 
  CheckCircle 
} from "lucide-react"

// Import modular portal views
import RecruiterDashboard from "./RecruiterDashboard"
import CandidateSearch from "./CandidateSearch"
import JobUpload from "./JobUpload"
import CandidateProfile from "./CandidateProfile"

function RecruiterConsole() {
  const [currentView, setCurrentView] = useState("dashboard") // dashboard | candidates | jobs | shortlist | candidate-profile
  const [selectedCandidateId, setSelectedCandidateId] = useState(null)
  
  // Track shortlists to display live count badge
  const [shortlist, setShortlist] = useState({ candidates: [] })
  const [loading, setLoading] = useState(false)

  const loadShortlist = async () => {
    setLoading(true)
    try {
      const sl = await getRecruiterShortlist()
      setShortlist(sl)
    } catch (err) {
      console.error("Failed to load shortlist:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadShortlist()
  }, [currentView])

  return (
    <div className="space-y-8 pb-12">
      {/* Title */}
      <div>
        <h1 className="text-5xl font-black bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent tracking-tight">
          Recruiter Talent Console
        </h1>
        <p className="text-gray-400 mt-2 text-sm font-medium">
          Query candidate profiles semantically, inspect ATS compatibility, manage job descriptions, and view pipeline analytics.
        </p>
      </div>

      {/* Navigation tabs */}
      <div className="flex border-b border-white/10 gap-6">
        {[
          { key: "dashboard", label: "Dashboard" },
          { key: "candidates", label: "Talent Directory" },
          { key: "jobs", label: "Job Roles" },
          { key: "shortlist", label: `Pipeline (${shortlist.candidates?.length || 0})` },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => {
              setCurrentView(tab.key)
              setSelectedCandidateId(null)
            }}
            className={`pb-3 font-semibold text-xs uppercase tracking-wider transition-all border-b-2 cursor-pointer ${
              currentView === tab.key 
                ? "border-blue-500 text-blue-400 font-bold" 
                : "border-transparent text-gray-500 hover:text-gray-300"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* View Content Panel */}
      <div className="mt-4">
        {currentView === "dashboard" && (
          <RecruiterDashboard onViewChange={(view) => setCurrentView(view)} />
        )}
        
        {currentView === "candidates" && (
          <CandidateSearch 
            onInspectCandidate={(id) => {
              setSelectedCandidateId(id)
              setCurrentView("candidate-profile")
            }} 
          />
        )}

        {currentView === "jobs" && (
          <JobUpload />
        )}

        {currentView === "candidate-profile" && selectedCandidateId && (
          <CandidateProfile 
            candidateId={selectedCandidateId} 
            onBack={() => {
              setSelectedCandidateId(null)
              setCurrentView("candidates")
            }} 
          />
        )}

        {currentView === "shortlist" && (
          loading ? (
            <div className="flex justify-center items-center py-20">
              <RefreshCw className="animate-spin text-blue-400" size={32} />
            </div>
          ) : shortlist.candidates.length === 0 ? (
            <div className="bg-slate-900/60 border border-white/5 p-16 rounded-3xl text-center text-gray-500 text-xs italic max-w-xl mx-auto backdrop-blur-xl">
              <UserCheck size={40} className="mx-auto text-gray-600 mb-4 animate-pulse" />
              No candidates have been shortlisted in your pipeline yet.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fadeIn">
              {shortlist.candidates.map((cand) => (
                <div
                  key={cand.resume_id}
                  onClick={() => {
                    setSelectedCandidateId(cand.resume_id)
                    setCurrentView("candidate-profile")
                  }}
                  className="bg-slate-900/60 border border-white/5 hover:border-blue-500/20 p-6 rounded-3xl backdrop-blur-xl flex flex-col justify-between hover:scale-[1.01] transition-all duration-300 group cursor-pointer"
                >
                  <div className="space-y-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-gray-200 text-base leading-snug group-hover:text-blue-400 transition">
                          {cand.filename}
                        </h4>
                        <span className="text-xs text-gray-400 block mt-1">{cand.user_email}</span>
                      </div>
                      <span className="shrink-0 px-2.5 py-1 bg-green-500/10 text-green-400 border border-green-500/10 rounded-xl text-[10px] font-black flex items-center gap-1">
                        <CheckCircle size={10} /> ATS: {cand.ats_score}%
                      </span>
                    </div>
                    
                    <div className="p-3.5 bg-slate-950/40 border border-white/5 rounded-2xl text-xs text-gray-400 leading-relaxed">
                      <strong className="text-gray-300">Pipeline Notes: </strong>{cand.notes || "Added to shortlist"}
                    </div>
                    
                    <div className="text-[10px] text-gray-500 font-semibold uppercase tracking-wider">
                      Added to pipeline: {cand.added_at ? cand.added_at.slice(0, 10) : "Recent"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )
        )}
      </div>
    </div>
  )
}

export default RecruiterConsole
