import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useNavigate } from "react-router-dom"
import { uploadResume, getPreviewUrl } from "../services/resumeApi"
import { useAnalysisFlow } from "../hooks/useAnalysisFlow"
import { useToast } from "../context/ToastContext"
import { useResume } from "../context/ResumeContext"
import { 
  CloudUpload, 
  FileText, 
  Play, 
  RefreshCw, 
  ChevronRight, 
  Sparkles, 
  AlertCircle, 
  Award, 
  Briefcase, 
  PenTool, 
  MessageSquare,
  LayoutGrid,
  CheckCircle2,
  TrendingUp,
  FileCheck,
  Zap,
  Gauge
} from "lucide-react"

import ATSCard from "../components/workspace/ATSCard"
import AICoach from "../components/AICoach"
import LiveProgress from "../components/workspace/LiveProgress"

function UploadFlow() {
  const navigate = useNavigate()
  const { showToast } = useToast()
  const { refreshResumes, setActiveResume } = useResume()
  const {
    status,
    setStatus,
    currentStage,
    currentStageIndex,
    totalStages,
    error,
    setError,
    analysisResult,
    runAnalysis,
    resetFlow,
    isBgProcessing,
    bgProgress,
    bgStatus,
    bgMessage
  } = useAnalysisFlow()

  const [file, setFile] = useState(null)
  const [resumeId, setResumeId] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [dragging, setDragging] = useState(false)
  const [activeTab, setActiveTab] = useState("feedback")

  // Sync active resume to global context once analysis completes successfully
  useEffect(() => {
    if (status === "completed" && resumeId) {
      const selectNewResume = async () => {
        try {
          const list = await refreshResumes()
          if (Array.isArray(list)) {
            const matched = list.find(r => r.id === resumeId)
            if (matched) {
              setActiveResume(matched)
              showToast("Analyzed resume set as active in workspace.", "success")
            } else {
              // Fallback if not found in list yet
              setActiveResume({
                id: resumeId,
                name: file?.name || "Uploaded Resume",
                score: `${analysisResult?.ats_score || 0}%`
              })
            }
          }
        } catch (err) {
          console.error("Failed to select active resume in workspace:", err)
        }
      }
      selectNewResume()
    }
  }, [status, resumeId, analysisResult])

  // Document Upload
  const handleUpload = async (selectedFile) => {
    if (!selectedFile) return
    setUploading(true)
    setError("")
    try {
      const res = await uploadResume(selectedFile)
      if (res.error) {
        setStatus("failed")
        setError(res.error)
        showToast(res.error, "error")
      } else {
        setFile(selectedFile)
        setResumeId(res.id)
        setStatus("uploaded")
        showToast("File uploaded successfully. Preview is loaded.", "success")
      }
    } catch (err) {
      setStatus("failed")
      setError("Failed to upload file. Please check connection.")
      showToast("File upload failed.", "error")
    } finally {
      setUploading(false)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    handleUpload(selectedFile)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => {
    setDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    handleUpload(droppedFile)
  }

  const handleStartAnalysis = async () => {
    if (!resumeId) return
    showToast("Launching background AI analysis pipelines...", "info")
    await runAnalysis(resumeId)
  }

  const handleReset = () => {
    setFile(null)
    setResumeId(null)
    resetFlow()
  }

  // Preview URL builder
  const previewUrl = resumeId ? getPreviewUrl(resumeId) : null
  const isPdf = file?.type === "application/pdf" || file?.name?.toLowerCase().endsWith(".pdf")

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Header section */}
      <div className="flex justify-between items-center mb-8 pb-6 border-b border-white/5">
        <div>
          <h1 className="text-4xl font-extrabold flex items-center gap-3">
            <Sparkles className="text-blue-400" /> AI Resume Intelligence
          </h1>
          <p className="text-gray-400 text-sm mt-1.5">
            Sequential enterprise-grade upload, preview, and multidimensional AI analysis workflow.
          </p>
        </div>
        {status !== "idle" && (
          <button
            onClick={handleReset}
            className="px-5 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-bold text-gray-300 rounded-xl transition cursor-pointer"
          >
            Clear and Upload New
          </button>
        )}
      </div>

      <AnimatePresence mode="wait">
        {/* STEP 1: UPLOAD AREA (IDLE) */}
        {status === "idle" && !uploading && (
          <motion.div
            key="upload"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              p-16 rounded-3xl border-2 border-dashed text-center transition-all duration-300 cursor-pointer max-w-2xl mx-auto
              ${dragging
                ? "border-blue-500 bg-blue-500/10 scale-102"
                : "border-white/10 bg-white/5 backdrop-blur-lg hover:border-blue-500/20"
              }
            `}
          >
            <div className="w-16 h-16 bg-blue-500/10 border border-blue-500/25 text-blue-400 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/5">
              <CloudUpload size={32} />
            </div>
            <h2 className="text-2xl font-bold text-gray-100 mb-2">Drag & Drop Resume</h2>
            <p className="text-gray-400 text-sm mb-6">PDF, DOC, or DOCX formats accepted</p>
            <label className="inline-flex bg-blue-500 hover:bg-blue-600 px-6 py-3 rounded-xl transition cursor-pointer font-bold text-sm text-white shadow-lg shadow-blue-500/20">
              Select File from Device
              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </motion.div>
        )}

        {/* LOADING UPLOAD */}
        {uploading && (
          <motion.div
            key="uploading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-white/5 backdrop-blur-lg border border-white/10 p-16 rounded-3xl text-center max-w-xl mx-auto space-y-4"
          >
            <RefreshCw className="animate-spin text-blue-400 mx-auto" size={32} />
            <p className="text-gray-300 font-semibold">Streaming document to secure database...</p>
          </motion.div>
        )}

        {/* STEP 2 & 3: PREVIEW & TRIGGER ANALYZE */}
        {status === "uploaded" && (
          <motion.div
            key="preview-flow"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="space-y-6"
          >
            {/* FULL RESUME PREVIEW */}
            <div className="bg-slate-900/60 border border-white/5 rounded-3xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-white/5 pb-4">
                <div className="flex items-center gap-2">
                  <FileText className="text-blue-400" size={20} />
                  <h3 className="text-lg font-bold text-gray-200">Uploaded Resume Preview</h3>
                </div>
                <span className="bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full text-xs font-semibold">
                  {file?.name}
                </span>
              </div>

              <div className="h-[600px] bg-slate-950/40 rounded-2xl border border-white/10 overflow-hidden">
                {isPdf ? (
                  <iframe src={previewUrl} className="w-full h-full border-none" title="Resume Preview" />
                ) : (
                  <div className="flex flex-col items-center justify-center h-full space-y-4 text-center">
                    <FileText size={48} className="text-gray-600" />
                    <p className="text-gray-400 text-sm">Preview only supported for PDF documents.</p>
                  </div>
                )}
              </div>
            </div>

            {/* ANALYZE BUTTON (STEP 3) */}
            <div className="flex justify-center pt-2">
              <button
                onClick={handleStartAnalysis}
                className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white font-bold py-3.5 px-8 rounded-xl text-sm transition cursor-pointer shadow-lg shadow-blue-500/20"
              >
                <Play size={16} fill="currentColor" />
                Analyze Resume Details
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 4: PROCESS LOADER */}
        {status === "analyzing" && (
          <div className="py-6">
            <LiveProgress 
              status={isBgProcessing ? bgStatus : "analyzing"} 
              progress={isBgProcessing ? bgProgress : Math.round(((currentStageIndex + 1) / totalStages) * 100)}
              message={isBgProcessing ? bgMessage : currentStage}
            />
          </div>
        )}

        {/* FAILURE STATE */}
        {status === "failed" && (
          <motion.div
            key="failed-flow"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-8 bg-rose-500/10 border border-rose-500/20 text-center rounded-3xl max-w-lg mx-auto space-y-5"
          >
            <AlertCircle className="text-rose-400 mx-auto" size={40} />
            <h3 className="text-xl font-bold text-rose-400">Analysis Failed</h3>
            <p className="text-gray-300 text-sm leading-relaxed">{error}</p>
            <div className="flex gap-4 justify-center pt-2">
              <button
                onClick={handleReset}
                className="px-5 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl text-xs font-bold transition cursor-pointer"
              >
                Upload Different Resume
              </button>
              <button
                onClick={handleStartAnalysis}
                className="px-5 py-2.5 bg-rose-500 hover:bg-rose-600 text-white rounded-xl text-xs font-bold transition cursor-pointer"
              >
                Retry Analysis
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 5: FULL SEMANTIC SUMMARY DASHBOARD */}
        {status === "completed" && analysisResult && (
          <motion.div
            key="completed-results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-8 animate-fadeIn"
          >
            {/* Sync Alert & Header */}
            <div className="p-5 bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20 rounded-3xl flex flex-col md:flex-row items-center justify-between gap-4 backdrop-blur-md shadow-lg shadow-emerald-500/5">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center">
                  <CheckCircle2 size={22} />
                </div>
                <div>
                  <h3 className="text-sm font-extrabold text-emerald-400">AI Intelligence Core Synced</h3>
                  <p className="text-[11px] text-gray-400 mt-0.5">Resume parsed, ATS score calculated, and semantic profiles created successfully.</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-[10px] bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-full font-bold">
                  Active in Workspace
                </span>
                <button
                  onClick={handleReset}
                  className="px-4 py-2 bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-bold text-gray-300 rounded-xl transition cursor-pointer"
                >
                  Upload New
                </button>
              </div>
            </div>

            {/* HERO DASHBOARD GRID */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Card 1: ATS SCORE & RECRUITER READINESS */}
              <div className="bg-slate-900/40 backdrop-blur-md p-6 rounded-3xl border border-white/5 space-y-6 flex flex-col justify-between shadow-xl">
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <Gauge size={16} className="text-blue-400" /> ATS Rating & Readiness
                  </h3>
                  <p className="text-[10px] text-gray-500">Overall suitability match score based on NLP parsing & career context</p>
                </div>

                <div className="flex flex-col items-center justify-center py-2 relative">
                  {/* Radial Gauge SVG */}
                  <svg className="w-36 h-36" viewBox="0 0 100 100">
                    <circle
                      className="text-white/5"
                      strokeWidth="8"
                      stroke="currentColor"
                      fill="transparent"
                      r="40"
                      cx="50"
                      cy="50"
                    />
                    <motion.circle
                      className="text-blue-500"
                      strokeWidth="8"
                      strokeDasharray={2 * Math.PI * 40}
                      strokeDashoffset={2 * Math.PI * 40 * (1 - (analysisResult.ats_score || 0) / 100)}
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="transparent"
                      r="40"
                      cx="50"
                      cy="50"
                      initial={{ strokeDashoffset: 2 * Math.PI * 40 }}
                      animate={{ strokeDashoffset: 2 * Math.PI * 40 * (1 - (analysisResult.ats_score || 0) / 100) }}
                      transition={{ duration: 1.5, ease: "easeOut" }}
                      style={{ transform: "rotate(-90deg)", transformOrigin: "50% 50%" }}
                    />
                  </svg>
                  <div className="absolute flex flex-col items-center justify-center">
                    <span className="text-3xl font-black text-gray-100">{analysisResult.ats_score || 0}</span>
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider">ATS Score</span>
                  </div>
                </div>

                <div className="space-y-3 border-t border-white/5 pt-4">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-gray-400">Recruiter Readiness:</span>
                    <span className="font-extrabold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded text-[10px]">
                      {analysisResult.ai_feedback?.career_readiness || "Intermediate"}
                    </span>
                  </div>
                  {analysisResult.category_scores && Object.entries(analysisResult.category_scores).slice(0, 3).map(([key, val]) => (
                    <div key={key} className="space-y-1">
                      <div className="flex justify-between text-[10px]">
                        <span className="text-gray-500 capitalize">{key} Score</span>
                        <span className="text-gray-300 font-bold">{val}%</span>
                      </div>
                      <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500/50 rounded-full" style={{ width: `${val}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Card 2: ACTION CENTER (Quick Navigation Console) */}
              <div className="bg-slate-900/40 backdrop-blur-md p-6 rounded-3xl border border-white/5 space-y-6 flex flex-col justify-between shadow-xl">
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <Zap size={16} className="text-yellow-400" /> Connected Actions
                  </h3>
                  <p className="text-[10px] text-gray-500">Execute advanced AI pipelines powered by your resume data</p>
                </div>

                <div className="space-y-3 py-2">
                  {/* Action 1: Interview Prep */}
                  <button
                    onClick={() => {
                      localStorage.setItem("activeResumeId", resumeId)
                      navigate("/interviews")
                    }}
                    className="w-full flex items-center justify-between p-3.5 bg-cyan-500/5 hover:bg-cyan-500/10 border border-cyan-500/20 hover:border-cyan-500/40 rounded-2xl transition duration-300 group text-left cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-cyan-500/20 text-cyan-400 rounded-xl flex items-center justify-center group-hover:scale-105 transition">
                        <MessageSquare size={16} />
                      </div>
                      <div>
                        <span className="text-xs font-bold text-cyan-400 block">Launch Interview Prep</span>
                        <span className="text-[9px] text-gray-400 block mt-0.5">Start adaptive AI simulation sessions</span>
                      </div>
                    </div>
                    <ChevronRight size={14} className="text-cyan-500" />
                  </button>

                  {/* Action 2: Job Matching */}
                  <button
                    onClick={() => {
                      localStorage.setItem("activeResumeId", resumeId)
                      navigate("/live-jobs")
                    }}
                    className="w-full flex items-center justify-between p-3.5 bg-yellow-500/5 hover:bg-yellow-500/10 border border-yellow-500/20 hover:border-yellow-500/40 rounded-2xl transition duration-300 group text-left cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-yellow-500/20 text-yellow-400 rounded-xl flex items-center justify-center group-hover:scale-105 transition">
                        <Briefcase size={16} />
                      </div>
                      <div>
                        <span className="text-xs font-bold text-yellow-400 block">Match Target Jobs</span>
                        <span className="text-[9px] text-gray-400 block mt-0.5">Explore semantic job opportunities</span>
                      </div>
                    </div>
                    <ChevronRight size={14} className="text-yellow-500" />
                  </button>

                  {/* Action 3: AI Rewriter */}
                  <button
                    onClick={() => {
                      localStorage.setItem("activeResumeId", resumeId)
                      navigate("/rewriter")
                    }}
                    className="w-full flex items-center justify-between p-3.5 bg-emerald-500/5 hover:bg-emerald-500/10 border border-emerald-500/20 hover:border-emerald-500/40 rounded-2xl transition duration-300 group text-left cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-emerald-500/20 text-emerald-400 rounded-xl flex items-center justify-center group-hover:scale-105 transition">
                        <PenTool size={16} />
                      </div>
                      <div>
                        <span className="text-xs font-bold text-emerald-400 block">Refine with AI Rewriter</span>
                        <span className="text-[9px] text-gray-400 block mt-0.5">Enhance section descriptions & bullets</span>
                      </div>
                    </div>
                    <ChevronRight size={14} className="text-emerald-500" />
                  </button>
                </div>

                <button
                  onClick={() => navigate("/")}
                  className="w-full flex items-center justify-center gap-2 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 text-xs font-bold text-gray-300 rounded-xl transition cursor-pointer"
                >
                  <LayoutGrid size={14} /> Save & Open Workspace Dashboard
                </button>
              </div>

              {/* Card 3: KEY COMPETENCIES & VULNERABILITIES */}
              <div className="bg-slate-900/40 backdrop-blur-md p-6 rounded-3xl border border-white/5 space-y-5 flex flex-col justify-between shadow-xl">
                <div className="space-y-2">
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <TrendingUp size={16} className="text-teal-400" /> Key Skills & Gaps
                  </h3>
                  <p className="text-[10px] text-gray-500">Core technologies vs. missing market requirements</p>
                </div>

                <div className="space-y-4 flex-1 mt-2">
                  {/* Strengths */}
                  <div className="space-y-2">
                    <h4 className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider">Top Competencies</h4>
                    <div className="flex flex-wrap gap-1.5 max-h-[85px] overflow-y-auto pr-1 scrollbar-thin">
                      {(analysisResult.parsed_data?.skills || []).slice(0, 8).map((skill, i) => (
                        <span key={i} className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded text-[10px] font-bold">
                          {skill}
                        </span>
                      ))}
                      {(analysisResult.parsed_data?.skills || []).length === 0 && (
                        <span className="text-[10px] text-gray-500 italic">No skills extracted</span>
                      )}
                    </div>
                  </div>

                  {/* Gaps */}
                  <div className="space-y-2 border-t border-white/5 pt-3">
                    <h4 className="text-[10px] font-bold text-rose-400 uppercase tracking-wider">Critical Skill Gaps</h4>
                    <div className="flex flex-wrap gap-1.5 max-h-[85px] overflow-y-auto pr-1 scrollbar-thin">
                      {(analysisResult.parsed_data?.missing_skills || []).slice(0, 8).map((skill, i) => (
                        <span key={i} className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-2 py-0.5 rounded text-[10px] font-bold">
                          {skill}
                        </span>
                      ))}
                      {(analysisResult.parsed_data?.missing_skills || []).length === 0 && (
                        <span className="text-[10px] text-gray-500 italic">None detected</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* TABBED REPORTS VIEW */}
            <div className="space-y-6">
              {/* Tab Header Selector */}
              <div className="flex border-b border-white/5">
                {[
                  { id: "feedback", label: "AI Coach Insights", icon: Sparkles },
                  { id: "nlp", label: "Semantic NLP Audit", icon: FileCheck },
                  { id: "layout", label: "Design & Preview", icon: LayoutGrid }
                ].map((tab) => {
                  const Icon = tab.icon
                  const active = activeTab === tab.id
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                        flex items-center gap-2 px-6 py-3 border-b-2 font-extrabold text-xs transition cursor-pointer
                        ${active
                          ? "border-blue-500 text-blue-400 bg-blue-500/5"
                          : "border-transparent text-gray-400 hover:text-gray-300"
                        }
                      `}
                    >
                      <Icon size={14} />
                      {tab.label}
                    </button>
                  )
                })}
              </div>

              {/* Tab Content Panels */}
              <AnimatePresence mode="wait">
                {activeTab === "feedback" && (
                  <motion.div
                    key="tab-feedback"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="space-y-6"
                  >
                    <AICoach feedback={analysisResult.ai_feedback} />
                  </motion.div>
                )}

                {activeTab === "nlp" && (
                  <motion.div
                    key="tab-nlp"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="space-y-6"
                  >
                    {analysisResult.extracted_entities && (
                      <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 space-y-6">
                        <h3 className="text-md font-bold text-gray-200 flex items-center gap-2">
                          <Sparkles size={16} className="text-cyan-400" /> Named Entity & Semantic NLP Insights
                        </h3>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {/* Entity Tags */}
                          <div className="space-y-4">
                            <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Extracted Entities (NER)</h4>
                            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 scrollbar-thin">
                              {[
                                { label: "Programming Languages", key: "programming_languages" },
                                { label: "Frameworks & Libraries", key: "frameworks" },
                                { label: "Cloud & Devops", key: "cloud_platforms" },
                                { label: "Tools", key: "tools" },
                                { label: "Technologies", key: "technologies" },
                                { label: "Degrees", key: "degrees" },
                                { label: "Universities", key: "universities" },
                                { label: "Companies", key: "companies" },
                                { label: "Locations", key: "locations" },
                                { label: "Certifications", key: "certifications" },
                                { label: "Experience Years", key: "years_of_experience" }
                              ].map((item, idx) => {
                                const list = analysisResult.extracted_entities[item.key] || [];
                                if (list.length === 0) return null;
                                return (
                                  <div key={idx} className="bg-slate-950/40 p-3 rounded-xl border border-white/5 space-y-1">
                                    <span className="text-[9px] text-gray-500 font-bold uppercase">{item.label}</span>
                                    <div className="flex flex-wrap gap-1.5">
                                      {list.map((ent, i) => (
                                        <span key={i} className="bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded text-[9px] font-bold">
                                          {ent.value} <span className="text-[7px] text-cyan-500/80">({Math.round(ent.confidence * 100)}%)</span>
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )
                              })}
                            </div>
                          </div>
                          
                          {/* Section Classifier & Action Verbs */}
                          <div className="space-y-6">
                            {/* Section Classifier Confidences */}
                            {analysisResult.section_confidences && (
                              <div className="space-y-3">
                                <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider">Semantic Section Analysis</h4>
                                <div className="grid grid-cols-2 gap-3 text-[10px]">
                                  {Object.entries(analysisResult.section_confidences).map(([section, confidence]) => (
                                    <div key={section} className="flex justify-between items-center bg-slate-950/30 p-2 rounded border border-white/5">
                                      <span className="text-gray-400 capitalize">{section}</span>
                                      <span className="text-purple-400 font-bold">{Math.round(confidence * 100)}% Match</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {/* Formatting Diagnostics */}
                            {analysisResult.section_diagnostics && (
                              <div className="space-y-3">
                                <h4 className="text-xs font-bold text-yellow-400 uppercase tracking-wider">Structural Diagnostics</h4>
                                <div className="p-4 bg-slate-950/30 border border-white/5 rounded-xl text-[11px] space-y-2">
                                  <div className="flex justify-between">
                                    <span className="text-gray-400">Merged Sections:</span>
                                    <span className="font-bold text-gray-200">
                                      {analysisResult.section_diagnostics.merged_sections?.length > 0 
                                        ? analysisResult.section_diagnostics.merged_sections.join(", ") 
                                        : "None Detected"}
                                    </span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-400">Duplicate Sections:</span>
                                    <span className="font-bold text-gray-200">
                                      {analysisResult.section_diagnostics.duplicate_sections?.length > 0 
                                        ? analysisResult.section_diagnostics.duplicate_sections.join(", ") 
                                        : "None Detected"}
                                    </span>
                                  </div>
                                  <div className="flex justify-between">
                                    <span className="text-gray-400">Unordered Sections:</span>
                                    <span className={`font-bold ${analysisResult.section_diagnostics.unordered_resume ? "text-rose-400" : "text-emerald-400"}`}>
                                      {analysisResult.section_diagnostics.unordered_resume ? "Anomaly Detected" : "Standard Order"}
                                    </span>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}

                {activeTab === "layout" && (
                  <motion.div
                    key="tab-layout"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="space-y-6"
                  >
                    {/* Visual Layout Audit */}
                    {analysisResult.multimodal_analysis && (
                      <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 space-y-6">
                        <h3 className="text-md font-bold text-gray-200 flex items-center gap-2">
                          <LayoutGrid size={16} className="text-purple-400" /> Gemini Vision Visual Layout Diagnostics
                        </h3>
                        
                        {/* Score breakdown metrics cards */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          {[
                            { label: "Layout Quality", score: analysisResult.multimodal_analysis.visual_scores?.layout_score },
                            { label: "Design Consistency", score: analysisResult.multimodal_analysis.visual_scores?.design_score },
                            { label: "Readability Spacing", score: analysisResult.multimodal_analysis.visual_scores?.readability_score },
                            { label: "Formatting Alignment", score: analysisResult.multimodal_analysis.visual_scores?.formatting_score },
                          ].map((dim, i) => (
                            <div key={i} className="bg-slate-950/60 p-4 rounded-xl border border-white/5 flex flex-col justify-between h-20">
                              <span className="text-[9px] text-gray-500 font-bold leading-tight uppercase block">{dim.label}</span>
                              <span className="text-2xl font-extrabold text-blue-400 block mt-2">{dim.score}%</span>
                            </div>
                          ))}
                        </div>

                        <div className="p-4 bg-slate-950/40 border border-white/5 rounded-2xl space-y-1 text-xs leading-relaxed">
                          <span className="font-bold text-purple-400">Layout Feedback Summary</span>
                          <p className="text-gray-300">
                            {analysisResult.multimodal_analysis.layout_feedback}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* Resume Preview */}
                    <div className="bg-slate-900/40 p-6 rounded-3xl border border-white/5 space-y-4">
                      <h3 className="text-md font-bold text-gray-200 flex items-center gap-2">
                        <FileText size={16} className="text-blue-400" /> Resume Document Preview
                      </h3>
                      <div className="h-[500px] bg-slate-950/40 rounded-2xl border border-white/10 overflow-hidden">
                        {isPdf ? (
                          <iframe src={previewUrl} className="w-full h-full border-none" title="Result Preview" />
                        ) : (
                          <div className="flex flex-col items-center justify-center h-full text-center">
                            <FileText size={40} className="text-gray-600 mb-2" />
                            <p className="text-gray-400 text-xs">{file?.name}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default UploadFlow
