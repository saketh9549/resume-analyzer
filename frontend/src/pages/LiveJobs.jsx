import { useState, useEffect } from "react"
import { useToast } from "../context/ToastContext"
import { useResume } from "../context/ResumeContext"
import { useCareerPreferences } from "../context/CareerPreferenceContext"
import { getLiveJobs } from "../services/api"
import { 
  Briefcase, 
  MapPin, 
  DollarSign, 
  ExternalLink, 
  RefreshCw, 
  AlertCircle, 
  Search, 
  Sparkles, 
  BookOpen, 
  TrendingUp, 
  Award 
} from "lucide-react"
import ResumeSelector from "../components/ResumeSelector"

function LiveJobs() {
  const { showToast } = useToast()
  const { activeResume } = useResume()
  const { preferences } = useCareerPreferences()
  
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [skillsFilter, setSkillsFilter] = useState("")

  const loadData = async (skillsVal = "", resumeIdVal = "") => {
    setLoading(true)
    try {
      const jobData = await getLiveJobs(skillsVal, resumeIdVal)
      if (jobData && jobData.error) {
        showToast(`Failed to load live jobs: ${jobData.error}`, "error")
        setJobs([])
      } else {
        setJobs(jobData || [])
      }
    } catch (err) {
      console.error(err)
      showToast("An unexpected error occurred while loading page data.", "error")
    } finally {
      setLoading(false)
    }
  }

  // Load jobs on mount, activeResume changes, or preferences changes
  useEffect(() => {
    if (localStorage.getItem("token")) {
      loadData(skillsFilter, activeResume?.id || "")
    }
  }, [activeResume, preferences])

  const handleSearchSubmit = async (e) => {
    e.preventDefault()
    loadData(skillsFilter, activeResume?.id || "")
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Title / Headers */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Live Remote Jobs
          </h1>
          <p className="text-gray-400 mt-2 text-lg">
            Explore live remote positions matching your active resume and career preferences in real-time.
          </p>
        </div>

        {/* Global selector */}
        <div className="flex flex-col gap-1">
          <span className="text-xs font-semibold text-gray-400">Select Active Workspace Resume:</span>
          <ResumeSelector />
        </div>
      </div>

      {/* Sync preferences indicators summary */}
      {preferences && (preferences.preferred_roles?.length > 0 || preferences.preferred_industries?.length > 0) && (
        <div className="p-4 bg-blue-500/5 border border-blue-500/10 rounded-2xl flex flex-wrap gap-4 items-center text-xs text-gray-300">
          <span className="font-bold text-blue-400 uppercase tracking-wide">Preference Sync:</span>
          {preferences.preferred_roles?.length > 0 && (
            <span>Target Roles: <strong className="text-gray-100">{preferences.preferred_roles.join(", ")}</strong></span>
          )}
          {preferences.experience_level && (
            <span>Level: <strong className="text-gray-100">{preferences.experience_level}</strong></span>
          )}
          {preferences.remote_preference && (
            <span>Model: <strong className="text-gray-100">{preferences.remote_preference.toUpperCase()}</strong></span>
          )}
        </div>
      )}

      {/* Search Filter Bar */}
      <div className="bg-white/5 border border-white/10 p-5 rounded-3xl backdrop-blur-md">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-4 items-center">
          <div className="flex-1 w-full flex items-center gap-3 bg-slate-900 border border-white/10 px-5 py-3.5 rounded-2xl focus-within:border-blue-500 transition">
            <Search size={18} className="text-gray-400" />
            <input
              type="text"
              value={skillsFilter}
              onChange={(e) => setSkillsFilter(e.target.value)}
              placeholder="Filter jobs by specific skills (comma separated, e.g. React, Python, AWS)..."
              className="flex-1 bg-transparent text-gray-200 outline-none text-sm placeholder-gray-500 border-none focus:ring-0 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-6 py-3.5 bg-blue-500 hover:bg-blue-600 transition font-semibold rounded-2xl text-white cursor-pointer shadow-lg shadow-blue-500/20 shrink-0"
          >
            Filter Jobs
          </button>
        </form>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-24">
          <RefreshCw className="animate-spin text-blue-400" size={32} />
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-white/5 border border-white/10 p-16 rounded-3xl text-center space-y-4 max-w-xl mx-auto backdrop-blur-md">
          <AlertCircle size={40} className="mx-auto text-blue-400" />
          <h3 className="text-xl font-bold text-gray-200">No Matching Jobs</h3>
          <p className="text-gray-400 text-sm">
            Could not find any active postings matching your search filters. Try removing specific skill restrictions or updating settings.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {jobs.map((job) => {
            const score = job.match_percentage || 50
            const scoreColor = score >= 80 ? "text-green-400 bg-green-500/10 border-green-500/20" : score >= 65 ? "text-yellow-400 bg-yellow-500/10 border-yellow-500/20" : "text-gray-400 bg-white/5 border-white/10"
            return (
              <div
                key={job.id}
                className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md flex flex-col justify-between hover:border-blue-500/30 hover:shadow-xl hover:shadow-blue-500/5 transition duration-300 group"
              >
                <div className="space-y-4">
                  {/* Job Header */}
                  <div className="flex justify-between items-start gap-3">
                    <div className="overflow-hidden">
                      <h4 className="font-bold text-gray-200 text-base group-hover:text-blue-400 transition leading-snug truncate">
                        {job.title}
                      </h4>
                      <span className="text-xs text-gray-400 block mt-1">{job.company_name}</span>
                    </div>
                    {/* Score Badge */}
                    <span className={`shrink-0 px-2.5 py-1 rounded-xl border text-[11px] font-black ${scoreColor}`}>
                      {score}% Match
                    </span>
                  </div>

                  <p className="text-xs text-gray-400 leading-relaxed font-medium">
                    {job.description}
                  </p>

                  {/* Job Meta Info */}
                  <div className="flex flex-wrap gap-2 text-[10px]">
                    <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 border border-white/5 text-gray-400 font-semibold">
                      <MapPin size={10} className="text-blue-400" /> {job.candidate_required_location}
                    </span>
                    <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 border border-white/5 text-gray-400 font-semibold">
                      <DollarSign size={10} className="text-green-400" /> {job.salary}
                    </span>
                  </div>

                  {/* Match Explanations */}
                  {job.match_reasons?.length > 0 && (
                    <div className="space-y-1.5 pt-1 border-t border-white/5">
                      <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wide flex items-center gap-1">
                        <TrendingUp size={10} /> Why you match
                      </span>
                      <ul className="space-y-1 text-[11px] text-gray-300 list-disc list-inside font-medium leading-relaxed pl-1">
                        {job.match_reasons.slice(0, 3).map((r, i) => (
                          <li key={i} className="truncate">{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Skill Gaps Suggestions */}
                  {job.skill_gaps?.length > 0 && (
                    <div className="space-y-1.5 pt-1 border-t border-white/5">
                      <span className="text-[10px] font-bold text-yellow-400 uppercase tracking-wide flex items-center gap-1">
                        <Award size={10} /> Skill gaps identified
                      </span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {job.skill_gaps.slice(0, 3).map((g, i) => (
                          <span key={i} className="text-[10px] px-2 py-0.5 rounded bg-yellow-500/10 text-yellow-300 font-semibold border border-yellow-500/20">
                            {g.skill} (Gaps: -{g.impact})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Recommended Certifications */}
                  {job.recommended_certifications?.length > 0 && (
                    <div className="space-y-1 pt-1 border-t border-white/5">
                      <span className="text-[10px] font-bold text-purple-400 uppercase tracking-wide flex items-center gap-1">
                        <BookOpen size={10} /> Recommended Prep
                      </span>
                      <p className="text-[10px] text-gray-400 leading-normal">
                        Consider checking: <strong className="text-gray-200 font-semibold">{job.recommended_certifications[0].certification}</strong>
                      </p>
                    </div>
                  )}
                </div>

                <div className="pt-6">
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-blue-500/10 hover:bg-blue-500 text-blue-400 hover:text-white border border-blue-500/20 group-hover:border-blue-500/50 transition-all font-bold text-xs"
                  >
                    Apply & View Position <ExternalLink size={12} />
                  </a>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default LiveJobs
