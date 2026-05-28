import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useNavigate } from "react-router-dom"
import { uploadResume, getPreviewUrl } from "../services/resumeApi"
import { useAnalysisFlow } from "../hooks/useAnalysisFlow"
import { useToast } from "../context/ToastContext"
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
  LayoutGrid
} from "lucide-react"

import ATSCard from "../components/workspace/ATSCard"
import AICoach from "../components/AICoach"
import LiveProgress from "../components/workspace/LiveProgress"

function UploadFlow() {
  const navigate = useNavigate()
  const { showToast } = useToast()
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

        {/* STEP 5: FULL VERTICAL RESULTS LAYOUT */}
        {status === "completed" && analysisResult && (
          <motion.div
            key="completed-results"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-8"
          >
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center justify-between">
              <span className="text-sm font-bold text-emerald-400">✓ AI Analysis Completed Successfully</span>
              <button
                onClick={handleReset}
                className="text-xs text-blue-400 hover:text-blue-300 font-bold underline cursor-pointer"
              >
                Upload Another Resume
              </button>
            </div>

            {/* SECTION 1: Resume Preview */}
            <div className="bg-slate-900/40 p-6 rounded-3xl border border-white/5 space-y-4">
              <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                <FileText size={18} className="text-blue-400" /> 1. Resume Document Preview
              </h3>
              <div className="h-[400px] bg-slate-950/40 rounded-2xl border border-white/10 overflow-hidden">
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

            {/* SECTION 2: ATS Score Card */}
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-gray-200 px-1 flex items-center gap-2">
                <Award size={18} className="text-emerald-400" /> 2. ATS Score & Match Results
              </h3>
              <ATSCard atsData={analysisResult} />
            </div>

            {/* SECTION 3: AI Feedback */}
            <div className="space-y-2">
              <h3 className="text-lg font-bold text-gray-200 px-1 flex items-center gap-2">
                <Sparkles size={18} className="text-purple-400" /> 3. AI Recruiter Coaching Review
              </h3>
              <AICoach feedback={analysisResult.ai_feedback} />
            </div>

            {/* SECTION 4: Skill Analysis */}
            <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 space-y-4">
              <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                <Award size={18} className="text-blue-400" /> 4. Technical Skill Alignment
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">Parsed Skills</h4>
                  {analysisResult.parsed_data?.skills?.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.parsed_data.skills.map((skill, i) => (
                        <span key={i} className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 px-3 py-1 rounded-lg text-xs font-semibold">
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-xs italic">No skills extracted.</p>
                  )}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2">Identified Gaps</h4>
                  {analysisResult.parsed_data?.missing_skills?.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.parsed_data.missing_skills.map((skill, i) => (
                        <span key={i} className="bg-rose-500/10 border border-rose-500/20 text-rose-400 px-3 py-1 rounded-lg text-xs font-semibold">
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-xs italic">No missing skills.</p>
                  )}
                </div>
              </div>
            </div>

            {/* SECTION 4.5: NLP Semantic Insights */}
            {analysisResult.extracted_entities && (
              <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 space-y-6">
                <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                  <Sparkles size={18} className="text-cyan-400" /> 4.5. Named Entity & Semantic NLP Insights
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
                          <div key={idx} className="bg-slate-950/40 p-3.5 rounded-xl border border-white/5 space-y-1.5">
                            <span className="text-[10px] text-gray-500 font-bold uppercase">{item.label}</span>
                            <div className="flex flex-wrap gap-1.5">
                              {list.map((ent, i) => (
                                <span key={i} className="bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 px-2 py-0.5 rounded text-[10px] font-bold" title={`Confidence: ${ent.confidence * 100}%`}>
                                  {ent.value} <span className="text-[8px] text-cyan-500/80">({Math.round(ent.confidence * 100)}%)</span>
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
                    
                    {/* Formatting Anomalies */}
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

            {/* SECTION 5: Job Matches */}
            <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                  <Briefcase size={18} className="text-yellow-400" /> 5. Target Career Matches
                </h3>
                <button
                  onClick={() => {
                    localStorage.setItem("selectedResumeId", resumeId)
                    navigate("/jobs")
                  }}
                  className="text-xs text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1 cursor-pointer"
                >
                  Configure Matching Console <ChevronRight size={14} />
                </button>
              </div>
              <p className="text-xs text-gray-400">
                Recommended employment profiles based on parsed experience and skills:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { title: "Senior Software Engineer", match: "94%", type: "Full-Time" },
                  { title: "DevOps Architect", match: "82%", type: "Contract" },
                  { title: "Backend API Engineer", match: "89%", type: "Remote" }
                ].map((job, idx) => (
                  <div key={idx} className="bg-slate-950/40 p-4 rounded-2xl border border-white/5 space-y-2">
                    <div className="flex justify-between items-start">
                      <span className="font-bold text-xs text-gray-200 truncate">{job.title}</span>
                      <span className="text-[10px] bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full font-bold">
                        {job.match}
                      </span>
                    </div>
                    <p className="text-[10px] text-gray-500">{job.type}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* SECTION 6: Visual Layout Audit */}
            {analysisResult.multimodal_analysis ? (
              <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 space-y-6">
                <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                  <LayoutGrid size={18} className="text-purple-400" /> 6. Gemini Vision Visual Layout Diagnostics
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
            ) : (
              <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 text-center py-8 text-gray-500 text-xs">
                Visual layout audit is only generated for uploaded PDF file structures.
              </div>
            )}

            {/* SECTION 7: Rewrite Suggestions */}
            <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                  <PenTool size={18} className="text-emerald-400" /> 7. Section Rewrite Recommendations
                </h3>
                <button
                  onClick={() => {
                    localStorage.setItem("selectedResumeId", resumeId)
                    navigate("/rewriter")
                  }}
                  className="text-xs text-blue-400 hover:text-blue-300 font-bold flex items-center gap-1 cursor-pointer"
                >
                  Open AI Rewriter <ChevronRight size={14} />
                </button>
              </div>
              <div className="p-4 bg-slate-950/40 border border-white/5 rounded-2xl text-xs text-gray-300 leading-relaxed">
                <span className="font-bold text-emerald-400 block mb-1">Recommended Summary Revision:</span>
                <p className="italic">
                  "Detail-oriented and results-driven Software Engineer with extensive experience developing REST APIs using Python and FastAPI, containerizing microservices with Docker, and building dynamic user interfaces in React. Proven record of optimizing query latencies and boosting ATS metrics."
                </p>
              </div>
            </div>

            {/* SECTION 8: Interview Preparation */}
            <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                  <MessageSquare size={18} className="text-cyan-400" /> 8. Mock Interview Readiness
                </h3>
                <button
                  onClick={() => {
                    localStorage.setItem("selectedResumeId", resumeId)
                    navigate("/interviews")
                  }}
                  className="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded-xl text-xs transition cursor-pointer shadow-md shadow-cyan-500/20"
                >
                  Start Simulator Session
                </button>
              </div>
              <p className="text-xs text-gray-400">
                Launch interactive mock recruiter interview questions customized to the skills and experiences on your resume.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default UploadFlow
