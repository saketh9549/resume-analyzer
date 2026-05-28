import { useState, useEffect } from "react"
import { useToast } from "../context/ToastContext"
import { motion, AnimatePresence } from "framer-motion"
import { 
  getRecentUploads, 
  matchResumeJobs, 
  getStoredJobMatches, 
  matchCustomJD, 
  getJobRoadmap 
} from "../services/api"
import { 
  Briefcase, 
  Award, 
  Sparkles, 
  MapPin, 
  DollarSign, 
  AlertCircle, 
  CheckCircle2, 
  BookOpen, 
  ArrowRight, 
  ChevronRight, 
  TrendingUp, 
  RefreshCw, 
  FileText, 
  Target,
  BarChart3,
  ListTodo
} from "lucide-react"
import { 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar,
  Tooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts"

function JobMatching() {
  const { showToast } = useToast()
  // Resume states
  const [resumes, setResumes] = useState([])
  const [selectedResumeId, setSelectedResumeId] = useState("")
  const [loadingResumes, setLoadingResumes] = useState(true)

  // Matching states
  const [matchingData, setMatchingData] = useState(null)
  const [runningMatch, setRunningMatch] = useState(false)
  const [activeTab, setActiveTab] = useState("recommendations") // recommendations | custom-jd | visualizer

  // Modal roadmap states
  const [selectedRoadmapJob, setSelectedRoadmapJob] = useState(null)
  const [roadmapData, setRoadmapData] = useState(null)
  const [loadingRoadmap, setLoadingRoadmap] = useState(false)

  // Custom JD matching states
  const [customTitle, setCustomTitle] = useState("")
  const [customDescription, setCustomDescription] = useState("")
  const [customResult, setCustomResult] = useState(null)
  const [runningCustomMatch, setRunningCustomMatch] = useState(false)

  // Load preferences from settings/localstorage
  const getCareerPreferences = () => {
    const industries = localStorage.getItem("preferredIndustries") || ""
    const roles = localStorage.getItem("preferredRoles") || ""
    const level = localStorage.getItem("preferredExperienceLevel") || "Intermediate"
    const location = localStorage.getItem("preferredLocation") || "Remote"

    return {
      preferred_industries: industries.split(",").map(i => i.trim()).filter(Boolean),
      preferred_roles: roles.split(",").map(r => r.trim()).filter(Boolean),
      experience_level: level,
      location_preference: location
    }
  }

  // Load resumes dropdown
  useEffect(() => {
    async function loadResumes() {
      try {
        const data = await getRecentUploads()
        if (data && data.error) {
          showToast(`Failed to load resumes: ${data.error}`, "error")
          setResumes([])
        } else {
          setResumes(data || [])
          if (data && data.length > 0) {
            setSelectedResumeId(data[0].id)
            // Pre-fetch existing matches if any
            fetchExistingMatches(data[0].id)
          }
        }
      } catch (err) {
        console.error("Failed to load resumes:", err)
        showToast("An unexpected error occurred while loading resumes.", "error")
      } finally {
        setLoadingResumes(false)
      }
    }
    loadResumes()
  }, [])

  const fetchExistingMatches = async (resumeId) => {
    try {
      const existing = await getStoredJobMatches(resumeId)
      if (existing) {
        setMatchingData(existing)
      } else {
        setMatchingData(null)
      }
    } catch (err) {
      setMatchingData(null)
    }
  }

  const handleResumeSelect = (e) => {
    const id = e.target.value
    setSelectedResumeId(id)
    fetchExistingMatches(id)
    setCustomResult(null)
  }

  const handleRunMatch = async () => {
    if (!selectedResumeId) return
    setRunningMatch(true)
    try {
      const prefs = getCareerPreferences()
      const res = await matchResumeJobs(selectedResumeId, prefs)
      if (res && !res.error) {
        setMatchingData(res)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setRunningMatch(false)
    }
  }

  const handleRunCustomMatch = async (e) => {
    e.preventDefault()
    if (!selectedResumeId || !customTitle || !customDescription) return
    setRunningCustomMatch(true)
    try {
      const res = await matchCustomJD(selectedResumeId, {
        job_title: customTitle,
        job_description: customDescription,
        experience_level: localStorage.getItem("preferredExperienceLevel") || "Intermediate"
      })
      if (res && !res.error) {
        setCustomResult(res)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setRunningCustomMatch(false)
    }
  }

  const handleViewRoadmap = async (job) => {
    setSelectedRoadmapJob(job)
    setLoadingRoadmap(true)
    setRoadmapData(null)
    try {
      const res = await getJobRoadmap(selectedResumeId, job.job_title)
      if (res) {
        setRoadmapData(res)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingRoadmap(false)
    }
  }

  // Prepares data for Recharts visual comparison
  const getVisualizationData = () => {
    if (!matchingData || !matchingData.recommended_jobs) return []
    return matchingData.recommended_jobs.map(job => ({
      name: job.job_title,
      "Semantic similarity": job.semantic_similarity_score ?? job.project_score,
      "Keyword score": job.keyword_score ?? job.skills_score,
      "Context relevance": job.contextual_relevance_score ?? job.skills_score,
      "Recruiter relevance": job.recruiter_relevance_score ?? job.experience_score,
      "Match %": job.match_percentage
    }))
  };

  const getRadarData = () => {
    if (!matchingData || !matchingData.recommended_jobs || matchingData.recommended_jobs.length === 0) return []
    const topJob = matchingData.recommended_jobs[0]
    return [
      { subject: "Semantic Similarity", value: topJob.semantic_similarity_score ?? topJob.project_score },
      { subject: "Keyword Coverage", value: topJob.keyword_score ?? topJob.skills_score },
      { subject: "Contextual Relevance", value: topJob.contextual_relevance_score ?? topJob.skills_score },
      { subject: "Recruiter Relevance", value: topJob.recruiter_relevance_score ?? topJob.experience_score }
    ]
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Title */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Career Intelligence
          </h1>
          <p className="text-gray-400 mt-2 text-lg">
            Evaluate resume compatibility against software job specs, analyze skill gaps, and build career roadmaps.
          </p>
        </div>

        {/* Dropdown Selector */}
        {!loadingResumes && resumes.length > 0 && (
          <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-3 rounded-2xl backdrop-blur-md">
            <FileText size={18} className="text-blue-400" />
            <select
              value={selectedResumeId}
              onChange={handleResumeSelect}
              className="bg-transparent text-gray-200 outline-none font-semibold text-sm cursor-pointer"
            >
              {resumes.map(r => (
                <option key={r.id} value={r.id} className="bg-slate-900 text-gray-200">
                  {r.name} ({r.score})
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {loadingResumes ? (
        <div className="flex justify-center items-center py-24">
          <RefreshCw className="animate-spin text-blue-400" size={32} />
        </div>
      ) : resumes.length === 0 ? (
        <div className="bg-white/5 border border-white/10 p-12 rounded-3xl text-center space-y-6 max-w-xl mx-auto backdrop-blur-md">
          <AlertCircle size={48} className="mx-auto text-blue-400" />
          <h2 className="text-2xl font-bold text-gray-200">No Resumes Found</h2>
          <p className="text-gray-400 text-sm">
            You must upload a parsed resume before evaluating career opportunities.
          </p>
          <a
            href="/upload"
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 font-semibold rounded-2xl text-white transition-all shadow-lg shadow-blue-500/20"
          >
            Go to Upload <ArrowRight size={16} />
          </a>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Main Navigation Tabs */}
          <div className="flex border-b border-white/10 gap-6">
            <button
              onClick={() => setActiveTab("recommendations")}
              className={`pb-3 font-semibold text-sm transition-all border-b-2 ${
                activeTab === "recommendations" ? "border-blue-500 text-blue-400 font-bold" : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              Job Recommendations
            </button>
            <button
              onClick={() => setActiveTab("custom-jd")}
              className={`pb-3 font-semibold text-sm transition-all border-b-2 ${
                activeTab === "custom-jd" ? "border-blue-500 text-blue-400 font-bold" : "border-transparent text-gray-400 hover:text-gray-200"
              }`}
            >
              Match Custom JD
            </button>
            {matchingData && (
              <button
                onClick={() => setActiveTab("visualizer")}
                className={`pb-3 font-semibold text-sm transition-all border-b-2 ${
                  activeTab === "visualizer" ? "border-blue-500 text-blue-400 font-bold" : "border-transparent text-gray-400 hover:text-gray-200"
                }`}
              >
                Compatibility Visualizer
              </button>
            )}
          </div>

          {/* recommendations TAB */}
          {activeTab === "recommendations" && (
            <div className="space-y-8">
              {!matchingData ? (
                <div className="bg-white/5 border border-white/10 p-12 rounded-3xl text-center space-y-6 max-w-xl mx-auto backdrop-blur-md">
                  <Target size={48} className="mx-auto text-blue-400" />
                  <h2 className="text-2xl font-bold text-gray-200">Evaluate Career Match</h2>
                  <p className="text-gray-400 text-sm">
                    Analyze this resume against modern technical career paths, calculate score alignments, and request personalized AI career recommendations.
                  </p>
                  <button
                    onClick={handleRunMatch}
                    disabled={runningMatch}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:cursor-not-allowed font-semibold rounded-2xl text-white transition-all cursor-pointer shadow-lg shadow-blue-500/20"
                  >
                    {runningMatch ? (
                      <>
                        <RefreshCw className="animate-spin" size={16} /> Evaluating Career Matches...
                      </>
                    ) : (
                      <>
                        <Sparkles size={16} /> Match Resume to Careers
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* Recommended Jobs List */}
                  <div className="lg:col-span-2 space-y-6">
                    <div className="flex justify-between items-center">
                      <h3 className="text-2xl font-bold flex items-center gap-2">
                        <Briefcase size={22} className="text-blue-400" /> Recommended Roles
                      </h3>
                      <button
                        onClick={handleRunMatch}
                        disabled={runningMatch}
                        className="flex items-center gap-1.5 text-sm text-blue-400 hover:text-blue-300 font-semibold cursor-pointer"
                      >
                        <RefreshCw size={14} className={runningMatch ? "animate-spin" : ""} /> Recalculate Matches
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {matchingData.recommended_jobs.map((job, idx) => (
                        <motion.div
                          key={job.job_title}
                          initial={{ opacity: 0, y: 15 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: idx * 0.05 }}
                          className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md flex flex-col justify-between hover:border-blue-500/30 transition-all group"
                        >
                          <div className="space-y-4">
                            {/* Card Header: Title + Gauge */}
                            <div className="flex justify-between items-start">
                              <div>
                                <h4 className="font-bold text-lg text-gray-200 group-hover:text-blue-400 transition">
                                  {job.job_title}
                                </h4>
                                <div className="flex items-center gap-1.5 mt-1 text-xs text-gray-400">
                                  <Award size={12} />
                                  <span>{job.readiness_level}</span>
                                </div>
                              </div>

                              {/* Circular Match Gauge */}
                              <div className="relative w-12 h-12 flex items-center justify-center">
                                <svg className="w-full h-full transform -rotate-90">
                                  <circle
                                    cx="24"
                                    cy="24"
                                    r="20"
                                    stroke="currentColor"
                                    strokeWidth="3"
                                    fill="transparent"
                                    className="text-white/5"
                                  />
                                  <circle
                                    cx="24"
                                    cy="24"
                                    r="20"
                                    stroke="currentColor"
                                    strokeWidth="3.5"
                                    fill="transparent"
                                    strokeDasharray="125.6"
                                    strokeDashoffset={125.6 - (125.6 * job.match_percentage) / 100}
                                    className={
                                      job.match_percentage >= 80 ? "text-green-400" :
                                      job.match_percentage >= 60 ? "text-yellow-400" : "text-blue-400"
                                    }
                                  />
                                </svg>
                                <span className="absolute text-[11px] font-black text-gray-200">
                                  {job.match_percentage}%
                                </span>
                              </div>
                            </div>

                            {/* Job Meta details */}
                            <div className="flex flex-wrap gap-2 text-xs">
                              <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 border border-white/5 text-gray-400">
                                <DollarSign size={10} /> {job.required_exp_years} yrs exp req
                              </span>
                              <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 border border-white/5 text-gray-400">
                                <MapPin size={10} /> Remote / Flexible
                              </span>
                            </div>

                            {/* Skill breakdown lists */}
                            <div className="space-y-3 pt-2">
                              {/* Matching Skills */}
                              <div>
                                <span className="block text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-1.5">Matching ({job.matching_skills.length})</span>
                                <div className="flex flex-wrap gap-1.5">
                                  {job.matching_skills.slice(0, 4).map(s => (
                                    <span key={s} className="px-2 py-0.5 rounded-lg bg-green-500/10 text-green-400 border border-green-500/10 text-[11px] font-semibold">
                                      {s}
                                    </span>
                                  ))}
                                  {job.matching_skills.length > 4 && (
                                    <span className="text-[10px] text-gray-500 self-center">+{job.matching_skills.length - 4} more</span>
                                  )}
                                </div>
                              </div>

                              {/* Missing Skills */}
                              {job.missing_skills.length > 0 && (
                                <div>
                                  <span className="block text-[11px] font-bold text-gray-500 uppercase tracking-wider mb-1.5">Missing ({job.missing_skills.length})</span>
                                  <div className="flex flex-wrap gap-1.5">
                                    {job.missing_skills.slice(0, 4).map(s => (
                                      <span key={s} className="px-2 py-0.5 rounded-lg bg-red-500/10 text-red-400 border border-red-500/10 text-[11px] font-semibold">
                                        {s}
                                      </span>
                                    ))}
                                    {job.missing_skills.length > 4 && (
                                      <span className="text-[10px] text-gray-500 self-center">+{job.missing_skills.length - 4} more</span>
                                    )}
                                  </div>
                                </div>
                              )}
                              {/* New 4-dimensional matching sub-scores breakdown */}
                              <div className="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-white/5 text-[10px]">
                                <div className="flex justify-between items-center bg-slate-950/20 px-2.5 py-1.5 rounded-lg border border-white/5">
                                  <span className="text-gray-400">Semantic Sim:</span>
                                  <span className="font-bold text-blue-400">{job.semantic_similarity_score ?? job.project_score}%</span>
                                </div>
                                <div className="flex justify-between items-center bg-slate-950/20 px-2.5 py-1.5 rounded-lg border border-white/5">
                                  <span className="text-gray-400">Keyword Fit:</span>
                                  <span className="font-bold text-emerald-400">{job.keyword_score ?? job.skills_score}%</span>
                                </div>
                                <div className="flex justify-between items-center bg-slate-950/20 px-2.5 py-1.5 rounded-lg border border-white/5">
                                  <span className="text-gray-400">Contextual:</span>
                                  <span className="font-bold text-purple-400">{job.contextual_relevance_score ?? job.skills_score}%</span>
                                </div>
                                <div className="flex justify-between items-center bg-slate-950/20 px-2.5 py-1.5 rounded-lg border border-white/5">
                                  <span className="text-gray-400">Recruiter Fit:</span>
                                  <span className="font-bold text-yellow-400">{job.recruiter_relevance_score ?? job.experience_score}%</span>
                                </div>
                              </div>
                            </div>
                          </div>
                          
                          <div className="pt-4">
                            <button
                              onClick={() => handleViewRoadmap(job)}
                              className="w-full flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-blue-500/10 hover:bg-blue-500 text-blue-400 hover:text-white transition-all font-semibold text-xs border border-blue-500/20 group-hover:border-blue-500/50 cursor-pointer"
                            >
                              <BookOpen size={13} /> View Learning Roadmap <ChevronRight size={13} />
                            </button>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* AI Career Coach Panel */}
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold flex items-center gap-2">
                      <Sparkles size={22} className="text-purple-400" /> AI Career Guidance
                    </h3>

                    <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md space-y-6">
                      {/* Summary text */}
                      <div className="space-y-2">
                        <span className="text-xs text-purple-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                          <Target size={14} /> Career Overview
                        </span>
                        <p className="text-gray-300 text-sm leading-relaxed">
                          {matchingData.career_guidance?.career_summary}
                        </p>
                      </div>

                      {/* Tracks */}
                      <div className="space-y-4 pt-2 border-t border-white/5">
                        <span className="text-xs text-purple-400 font-bold uppercase tracking-wider block">Recommended Career Tracks</span>
                        <div className="space-y-3">
                          {matchingData.career_guidance?.recommended_tracks?.map(track => (
                            <div key={track.role} className="p-3 bg-white/5 rounded-2xl border border-white/5 space-y-1.5">
                              <div className="flex justify-between items-center">
                                <h5 className="font-bold text-sm text-gray-200">{track.role}</h5>
                                <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 font-semibold">
                                  {track.salary_upside} Salary
                                </span>
                              </div>
                              <p className="text-xs text-gray-400 leading-relaxed">{track.alignment_reason}</p>
                              <div className="text-[10px] text-gray-500 font-medium">Difficulty: {track.difficulty}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Transition Guidance */}
                      <div className="space-y-2 pt-4 border-t border-white/5 text-sm">
                        <span className="text-xs text-purple-400 font-bold uppercase tracking-wider block">Transition Advice</span>
                        <p className="text-gray-300 leading-relaxed">
                          {matchingData.career_guidance?.transition_advice}
                        </p>
                      </div>

                      {/* Overall advice */}
                      {matchingData.career_guidance?.overall_guidance && (
                        <div className="p-4 bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs rounded-2xl leading-relaxed">
                          <strong>Coach Tip: </strong>{matchingData.career_guidance.overall_guidance}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* CUSTOM JD MATCH TAB */}
          {activeTab === "custom-jd" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
              {/* Form Input Card */}
              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6">
                <div>
                  <h3 className="text-2xl font-bold flex items-center gap-2">
                    <ListTodo size={22} className="text-blue-400" /> Custom Description Evaluator
                  </h3>
                  <p className="text-gray-400 text-xs mt-1.5">
                    Paste any software job specifications description to evaluate ATS fit and matching percentages immediately.
                  </p>
                </div>

                <form onSubmit={handleRunCustomMatch} className="space-y-5">
                  <div>
                    <label className="block text-sm text-gray-400 font-semibold mb-2">Job Title Target</label>
                    <input
                      type="text"
                      value={customTitle}
                      onChange={(e) => setCustomTitle(e.target.value)}
                      required
                      placeholder="e.g. Senior Frontend Engineer"
                      className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-gray-400 font-semibold mb-2">Full Job Description Text</label>
                    <textarea
                      value={customDescription}
                      onChange={(e) => setCustomDescription(e.target.value)}
                      required
                      rows={8}
                      placeholder="Paste the full job responsibilities, required technical skills, and experience details here..."
                      className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition text-sm leading-relaxed"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={runningCustomMatch}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:cursor-not-allowed font-semibold rounded-2xl text-white transition-all cursor-pointer shadow-lg shadow-blue-500/20"
                  >
                    {runningCustomMatch ? (
                      <>
                        <RefreshCw className="animate-spin" size={16} /> Evaluating Alignment...
                      </>
                    ) : (
                      <>
                        <Sparkles size={16} /> Match Custom Job Description
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Form Results Card */}
              <div>
                {!customResult ? (
                  <div className="bg-white/5 border border-white/10 border-dashed p-16 rounded-3xl text-center text-gray-400 text-sm backdrop-blur-md h-[480px] flex flex-col justify-center items-center">
                    <Target size={40} className="mb-4 text-gray-500" />
                    Fill in details and run evaluate to inspect match breakdowns.
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6"
                  >
                    {/* Header */}
                    <div className="flex justify-between items-center border-b border-white/5 pb-5">
                      <div>
                        <h4 className="font-bold text-xl text-gray-200">{customResult.job_title}</h4>
                        <span className="text-xs text-blue-400 font-semibold">{customResult.readiness_level}</span>
                      </div>
                      <div className="px-4 py-2 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-2xl font-black text-xl">
                        {customResult.match_percentage}%
                      </div>
                    </div>

                    {/* Breakdown gauges */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                      <div className="p-3 bg-white/5 rounded-2xl text-center">
                        <span className="block text-[10px] text-gray-400 font-semibold uppercase">Skills</span>
                        <span className="text-lg font-black text-gray-200">{customResult.skills_score}%</span>
                      </div>
                      <div className="p-3 bg-white/5 rounded-2xl text-center">
                        <span className="block text-[10px] text-gray-400 font-semibold uppercase">Experience</span>
                        <span className="text-lg font-black text-gray-200">{customResult.experience_score}%</span>
                      </div>
                      <div className="p-3 bg-white/5 rounded-2xl text-center">
                        <span className="block text-[10px] text-gray-400 font-semibold uppercase">Projects</span>
                        <span className="text-lg font-black text-gray-200">{customResult.project_score}%</span>
                      </div>
                      <div className="p-3 bg-white/5 rounded-2xl text-center">
                        <span className="block text-[10px] text-gray-400 font-semibold uppercase">ATS Quality</span>
                        <span className="text-lg font-black text-gray-200">{customResult.education_score}%</span>
                      </div>
                    </div>
                    {/* New 4-dimensional matching sub-scores breakdown for Custom JD */}
                    <div className="grid grid-cols-2 gap-3 mt-4 p-4 bg-slate-950/30 rounded-2xl border border-white/5 text-xs">
                      <div className="flex justify-between items-center bg-slate-950/40 p-2.5 rounded-xl border border-white/5">
                        <span className="text-gray-400">Semantic Similarity:</span>
                        <span className="font-bold text-blue-400">{customResult.semantic_similarity_score ?? customResult.project_score}%</span>
                      </div>
                      <div className="flex justify-between items-center bg-slate-950/40 p-2.5 rounded-xl border border-white/5">
                        <span className="text-gray-400">Keyword Coverage:</span>
                        <span className="font-bold text-emerald-400">{customResult.keyword_score ?? customResult.skills_score}%</span>
                      </div>
                      <div className="flex justify-between items-center bg-slate-950/40 p-2.5 rounded-xl border border-white/5">
                        <span className="text-gray-400">Contextual Relevance:</span>
                        <span className="font-bold text-purple-400">{customResult.contextual_relevance_score ?? customResult.skills_score}%</span>
                      </div>
                      <div className="flex justify-between items-center bg-slate-950/40 p-2.5 rounded-xl border border-white/5">
                        <span className="text-gray-400">Recruiter Relevance:</span>
                        <span className="font-bold text-yellow-400">{customResult.recruiter_relevance_score ?? customResult.experience_score}%</span>
                      </div>
                    </div>

                    {/* Skills found/missing */}
                    <div className="space-y-4 pt-2">
                      <div>
                        <span className="text-xs text-green-400 font-bold uppercase tracking-wider block mb-2">Matching Skills ({customResult.matching_skills.length})</span>
                        <div className="flex flex-wrap gap-2">
                          {customResult.matching_skills.map(s => (
                            <span key={s} className="px-2.5 py-1 rounded-xl bg-green-500/10 text-green-400 border border-green-500/10 text-xs font-semibold">
                              {s}
                            </span>
                          ))}
                          {customResult.matching_skills.length === 0 && <span className="text-xs text-gray-500">None detected.</span>}
                        </div>
                      </div>

                      <div>
                        <span className="text-xs text-red-400 font-bold uppercase tracking-wider block mb-2">Missing Skills ({customResult.missing_skills.length})</span>
                        <div className="flex flex-wrap gap-2">
                          {customResult.missing_skills.map(s => (
                            <span key={s} className="px-2.5 py-1 rounded-xl bg-red-500/10 text-red-400 border border-red-500/10 text-xs font-semibold">
                              {s}
                            </span>
                          ))}
                          {customResult.missing_skills.length === 0 && <span className="text-xs text-gray-500">No missing skills! Excellent matching.</span>}
                        </div>
                      </div>

                      {customResult.extra_skills.length > 0 && (
                        <div>
                          <span className="text-xs text-purple-400 font-bold uppercase tracking-wider block mb-2">Extra Skills ({customResult.extra_skills.length})</span>
                          <div className="flex flex-wrap gap-2">
                            {customResult.extra_skills.slice(0, 8).map(s => (
                              <span key={s} className="px-2.5 py-1 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/10 text-xs font-semibold">
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          )}

          {/* VISUALIZER TAB */}
          {activeTab === "visualizer" && matchingData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Radar comparison chart */}
              <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md space-y-4">
                <h4 className="text-lg font-bold flex items-center gap-1.5">
                  <Target size={18} className="text-blue-400" /> Career Match Fit Radar (Top Job)
                </h4>
                <div className="h-80 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart cx="50%" cy="50%" radius="70%" data={getRadarData()}>
                      <PolarGrid stroke="#ffffff10" />
                      <PolarAngleAxis dataKey="subject" tick={{ fill: "#94a3b8", fontSize: 11 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#94a3b8", fontSize: 10 }} />
                      <Radar
                        name="Match Quality"
                        dataKey="value"
                        stroke="#3b82f6"
                        fill="#3b82f6"
                        fillOpacity={0.2}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Bar comparison chart */}
              <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md space-y-4">
                <h4 className="text-lg font-bold flex items-center gap-1.5">
                  <BarChart3 size={18} className="text-blue-400" /> NLP Semantic Matching Metrics Breakdown
                </h4>
                <div className="h-80 w-full text-xs">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={getVisualizationData()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" />
                      <XAxis dataKey="name" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip 
                        contentStyle={{ backgroundColor: "#0f172a", borderColor: "#ffffff10", color: "#f8fafc" }}
                        itemStyle={{ color: "#f8fafc" }}
                      />
                      <Bar dataKey="Semantic similarity" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Keyword score" fill="#10b981" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Context relevance" fill="#a855f7" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Recruiter relevance" fill="#eab308" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Match %" fill="rgba(255, 255, 255, 0.2)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ROADMAP DETAIL MODAL */}
      <AnimatePresence>
        {selectedRoadmapJob && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedRoadmapJob(null)}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            />

            {/* Content card */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-2xl bg-slate-900 border border-white/10 p-8 rounded-3xl shadow-2xl overflow-y-auto max-h-[90vh] space-y-6"
            >
              {/* Header */}
              <div className="flex justify-between items-start border-b border-white/5 pb-4">
                <div>
                  <h4 className="text-2xl font-black text-gray-200">
                    {selectedRoadmapJob.job_title}
                  </h4>
                  <p className="text-xs text-gray-400 mt-1">
                    AI learning curriculum generated dynamically using Gemini
                  </p>
                </div>
                <button
                  onClick={() => setSelectedRoadmapJob(null)}
                  className="text-gray-400 hover:text-gray-200 text-lg cursor-pointer bg-white/5 w-8 h-8 rounded-full flex items-center justify-center border border-white/10"
                >
                  ✕
                </button>
              </div>

              {loadingRoadmap ? (
                <div className="flex flex-col items-center justify-center py-20 space-y-3">
                  <RefreshCw className="animate-spin text-blue-400" size={32} />
                  <span className="text-sm text-gray-400">Assembling curriculum steps...</span>
                </div>
              ) : !roadmapData ? (
                <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-2xl text-center">
                  Failed to fetch roadmap guidelines. Please try again.
                </div>
              ) : (
                <div className="space-y-6">
                  {/* Priority technology badges */}
                  <div className="space-y-2">
                    <span className="text-xs font-bold text-blue-400 uppercase tracking-wider block">Priority Tech Stack focus</span>
                    <div className="flex flex-wrap gap-2">
                      {roadmapData.priority_skills?.map(s => (
                        <span key={s} className="px-3 py-1 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-bold">
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Step list */}
                  <div className="space-y-5">
                    <span className="text-xs font-bold text-blue-400 uppercase tracking-wider block">Study Steps</span>
                    <div className="space-y-4">
                      {roadmapData.roadmap_steps?.map((step, idx) => (
                        <div key={idx} className="flex gap-4 p-4 bg-white/5 border border-white/5 rounded-2xl items-start">
                          <div className="w-8 h-8 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center font-black text-sm shrink-0">
                            {step.step || idx + 1}
                          </div>
                          <div className="space-y-2 flex-1">
                            <div className="flex justify-between items-start gap-2">
                              <h5 className="font-bold text-sm text-gray-200">{step.topic}</h5>
                              <span className="text-[10px] text-gray-500 font-semibold shrink-0">Duration: {step.timeline}</span>
                            </div>
                            <p className="text-xs text-gray-400 leading-relaxed">{step.description}</p>
                            
                            {/* Course suggestions */}
                            {step.recommended_courses_or_resources && step.recommended_courses_or_resources.length > 0 && (
                              <div className="flex flex-wrap items-center gap-1.5 pt-1">
                                <span className="text-[10px] text-gray-500 font-bold">Resources:</span>
                                {step.recommended_courses_or_resources.map(res => (
                                  <span key={res} className="text-[10px] text-gray-400 underline decoration-white/10 hover:text-white transition">
                                    {res}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Suggested certifications */}
                  {roadmapData.certification_suggestions && roadmapData.certification_suggestions.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-white/5">
                      <span className="text-xs font-bold text-blue-400 uppercase tracking-wider block">Recommended Certifications</span>
                      <ul className="list-disc list-inside text-xs text-gray-400 space-y-1">
                        {roadmapData.certification_suggestions.map((c, i) => (
                          <li key={i}>{c}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default JobMatching
