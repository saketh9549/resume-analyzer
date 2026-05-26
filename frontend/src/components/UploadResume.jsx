import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import ScoreGauge from "./ScoreGauge"
import AICoach from "./AICoach"
import AnalyzeButton from "./AnalyzeButton"
import AnalysisLoader from "./AnalysisLoader"
import { uploadResume, analyzeResumeAI, getParsedResume } from "../services/api"

function UploadResume() {
  const [file, setFile] = useState(null)
  const [resumeId, setResumeId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragging, setDragging] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [aiFeedback, setAiFeedback] = useState(null)
  
  // Workflow states: 'idle', 'uploaded', 'analyzing', 'completed', 'failed'
  const [workflowStatus, setWorkflowStatus] = useState("idle")
  const [activeTab, setActiveTab] = useState("overview")
  const [errorMsg, setErrorMsg] = useState("")

  async function handleUpload(selectedFile) {
    if (!selectedFile) return
    setLoading(true)
    setErrorMsg("")
    try {
      const response = await uploadResume(selectedFile)
      if (response.error) {
        setWorkflowStatus("failed")
        setErrorMsg(response.error)
      } else {
        setFile(selectedFile)
        setResumeId(response.id)
        setWorkflowStatus("uploaded")
      }
    } catch (err) {
      setWorkflowStatus("failed")
      setErrorMsg("Failed to upload resume. Please try again.")
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  async function handleAnalyze() {
    if (!resumeId) return
    setWorkflowStatus("analyzing")
    setErrorMsg("")
    try {
      const model = localStorage.getItem("aiModel") || "gemini-2.5-flash"
      const strictness = localStorage.getItem("aiStrictness") || "standard"

      // 1. Run Gemini AI feedback generator
      const aiResponse = await analyzeResumeAI(resumeId, model, strictness)
      
      if (aiResponse.error) {
        setWorkflowStatus("failed")
        setErrorMsg(aiResponse.error)
        return
      }

      // 2. Load Parsed Document structure (skills, education, experience, projects)
      const docResponse = await getParsedResume(resumeId)
      
      if (!docResponse) {
        setWorkflowStatus("failed")
        setErrorMsg("Failed to retrieve resume parsed data.")
        return
      }

      // Store states and complete workflow
      setAiFeedback(aiResponse.ai_feedback)
      setAnalysis(docResponse)
      setWorkflowStatus("completed")
      setActiveTab("overview")
    } catch (err) {
      setWorkflowStatus("failed")
      setErrorMsg("Failed to analyze resume. Please try again.")
      console.error(err)
    }
  }

  function handleFileChange(event) {
    const selectedFile = event.target.files[0]
    handleUpload(selectedFile)
  }

  function handleDragOver(event) {
    event.preventDefault()
    setDragging(true)
  }

  function handleDragLeave() {
    setDragging(false)
  }

  function handleDrop(event) {
    event.preventDefault()
    setDragging(false)
    const droppedFile = event.dataTransfer.files[0]
    handleUpload(droppedFile)
  }

  function handleReset() {
    setFile(null)
    setResumeId(null)
    setAnalysis(null)
    setAiFeedback(null)
    setWorkflowStatus("idle")
    setErrorMsg("")
  }

  return (
    <div>
      {/* HEADER SECTION */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-5xl font-bold">Upload Resume</h1>
          <p className="text-gray-400 mt-2 text-lg">
            Scan your credentials with Google Gemini AI audits.
          </p>
        </div>
        {workflowStatus !== "idle" && (
          <button
            onClick={handleReset}
            className="px-6 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 transition rounded-xl text-sm font-semibold cursor-pointer"
          >
            Clear / Upload New
          </button>
        )}
      </div>

      {/* BEFORE FILE UPLOADED (IDLE & LOADING STATE) */}
      {workflowStatus === "idle" && !loading && (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`
            p-20 rounded-3xl border-2 border-dashed text-center transition-all duration-300 cursor-pointer max-w-3xl mx-auto
            ${dragging
              ? "border-blue-500 bg-blue-500/10 scale-105"
              : "border-white/10 bg-white/5 backdrop-blur-lg"
            }
          `}
        >
          <div className="text-7xl mb-8">📄</div>
          <h2 className="text-5xl font-bold mb-6">Drag & Drop Resume</h2>
          <p className="text-gray-400 text-xl mb-8">Upload PDF, DOC, or DOCX files</p>
          <label
            className="inline-block bg-blue-500 hover:bg-blue-600 px-8 py-4 rounded-2xl transition cursor-pointer font-semibold text-lg"
          >
            Choose File
            <input
              type="file"
              accept=".pdf,.doc,.docx"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
        </div>
      )}

      {loading && (
        <div className="mt-10 bg-white/5 backdrop-blur-lg border border-white/10 p-16 rounded-3xl text-center max-w-4xl mx-auto space-y-4 animate-pulse">
          <div className="h-6 bg-slate-700 rounded w-1/3 mx-auto" />
          <div className="h-4 bg-slate-700 rounded w-2/3 mx-auto" />
          <p className="text-gray-400 text-lg pt-4">Uploading file details to server storage...</p>
        </div>
      )}

      {/* FAILURE STATE */}
      {workflowStatus === "failed" && (
        <div className="p-8 bg-red-500/10 border border-red-500/20 text-center rounded-3xl max-w-xl mx-auto space-y-6">
          <div className="text-5xl">⚠️</div>
          <h3 className="text-2xl font-bold text-red-400">Analysis Pipeline Failed</h3>
          <p className="text-gray-300 text-sm leading-relaxed">
            {errorMsg || "An unexpected error occurred during resume uploads or scoring audits."}
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={handleReset}
              className="px-6 py-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition font-semibold cursor-pointer"
            >
              Upload Different File
            </button>
            {resumeId && (
              <button
                onClick={handleAnalyze}
                className="px-6 py-3 rounded-2xl bg-red-500 hover:bg-red-600 text-white transition font-semibold cursor-pointer"
              >
                Retry Analysis
              </button>
            )}
          </div>
        </div>
      )}

      {/* UPLOADED, ANALYZING, & COMPLETED FLOW LAYOUT (SPLIT SCREEN LAYOUT) */}
      {(workflowStatus === "uploaded" || workflowStatus === "analyzing" || workflowStatus === "completed") && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-10 items-start">
          {/* LEFT SIDE PANEL (CTA / LOADER / RESULTS) */}
          <div className="w-full">
            <AnimatePresence mode="wait">
              {/* STATE A: FILE UPLOADED - PROMPT CTA */}
              {workflowStatus === "uploaded" && (
                <motion.div
                  key="uploaded"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                  className="bg-white/5 backdrop-blur-lg border border-white/10 p-8 rounded-3xl text-center space-y-6"
                >
                  <div className="text-6xl">🤖</div>
                  <h3 className="text-3xl font-extrabold text-white">Document Uploaded Successfully</h3>
                  <p className="text-gray-400 text-sm leading-relaxed max-w-sm mx-auto">
                    Your file <span className="font-semibold text-gray-200">"{file?.name}"</span> is queued. Click below to launch the Gemini AI Recruiter review and ATS scoring analysis.
                  </p>
                  <AnalyzeButton onClick={handleAnalyze} disabled={false} status={workflowStatus} />
                </motion.div>
              )}

              {/* STATE B: RUNNING ANALYSIS - LOADER SCREEN */}
              {workflowStatus === "analyzing" && (
                <motion.div
                  key="analyzing"
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -15 }}
                >
                  <AnalysisLoader />
                </motion.div>
              )}

              {/* STATE C: PROCESS COMPLETED - RESULTS CONTAINER */}
              {workflowStatus === "completed" && (
                <motion.div
                  key="completed"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="bg-white/5 backdrop-blur-lg border border-white/10 p-6 md:p-8 rounded-3xl shadow-2xl space-y-6"
                >
                  {/* Result Header */}
                  <div className="flex items-center justify-between border-b border-white/5 pb-4">
                    <div>
                      <h2 className="text-2xl font-bold">Analysis Results</h2>
                      <p className="text-xs text-gray-400 mt-0.5">{file?.name}</p>
                    </div>
                    <span className="bg-green-500/10 border border-green-500/20 text-green-400 px-3.5 py-1.5 rounded-full text-xs font-bold">
                      Completed
                    </span>
                  </div>

                  {/* Tabs Headers */}
                  <div className="flex border-b border-white/10 pb-1 gap-1 overflow-x-auto scrollbar-none">
                    {[
                      { id: "overview", label: "Overview" },
                      { id: "ai_insights", label: "AI Insights Coach" },
                      { id: "scoring", label: "Scoring Breakdown" },
                      { id: "experience", label: "Experience & Edu" },
                      { id: "projects", label: "Projects & Certs" }
                    ].map((tab) => (
                      <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`
                          pb-3 px-3 text-xs sm:text-sm font-semibold transition-all border-b-2 whitespace-nowrap cursor-pointer
                          ${activeTab === tab.id
                            ? "border-blue-500 text-blue-400"
                            : "border-transparent text-gray-400 hover:text-gray-200"
                          }
                        `}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>

                  {/* Tab Details */}
                  <div className="mt-4 max-h-[620px] overflow-y-auto pr-1">
                    {activeTab === "overview" && (
                      <div className="space-y-6">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-slate-900/70 p-5 rounded-2xl border border-white/5">
                            <p className="text-xs text-gray-400 font-semibold mb-1">ATS Match Score</p>
                            <p className="text-4xl font-extrabold text-blue-400">{analysis?.ats_score || 0}%</p>
                          </div>
                          <div className="bg-slate-900/70 p-5 rounded-2xl border border-white/5">
                            <p className="text-xs text-gray-400 font-semibold mb-1">Skills Found</p>
                            <p className="text-xs text-gray-200 truncate mt-1">
                              {analysis?.skills && analysis.skills.length > 0
                                ? analysis.skills.slice(0, 5).join(", ") + (analysis.skills.length > 5 ? "..." : "")
                                : "None parsed"}
                            </p>
                          </div>
                        </div>

                        <div className="flex justify-center py-4 bg-slate-900/40 rounded-2xl border border-white/5">
                          <ScoreGauge score={analysis?.ats_score || 0} />
                        </div>
                      </div>
                    )}

                    {activeTab === "ai_insights" && (
                      <AICoach feedback={aiFeedback} />
                    )}

                    {activeTab === "scoring" && (
                      <div className="space-y-5 bg-slate-900/40 p-5 rounded-2xl border border-white/5">
                        <h3 className="text-lg font-bold text-gray-200">ATS Scoring Dimension Breakdown</h3>
                        {analysis?.category_scores ? (
                          <div className="space-y-4">
                            {Object.entries(analysis.category_scores).map(([category, val]) => (
                              <div key={category} className="space-y-1">
                                <div className="flex justify-between text-xs">
                                  <span className="text-gray-300 font-medium capitalize">{category.replace(/_/g, ' ')}</span>
                                  <span className="font-bold text-blue-400">{val}%</span>
                                </div>
                                <div className="w-full bg-slate-900 rounded-full h-2.5">
                                  <div
                                    className="bg-blue-500 h-2.5 rounded-full transition-all duration-500"
                                    style={{ width: `${val}%` }}
                                  />
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-gray-500 text-sm">No scoring breakdowns parsed.</p>
                        )}
                      </div>
                    )}

                    {activeTab === "experience" && (
                      <div className="space-y-6">
                        <div>
                          <h3 className="text-base font-bold mb-3 text-blue-400">Professional History</h3>
                          {analysis?.experience && analysis.experience.length > 0 ? (
                            <div className="space-y-3">
                              {analysis.experience.map((job, idx) => (
                                <div key={idx} className="bg-slate-900/60 p-4 rounded-xl border border-white/5 text-sm space-y-2">
                                  <div className="flex justify-between items-start">
                                    <div>
                                      <h4 className="font-bold text-gray-200">{job.role || job.job_title}</h4>
                                      <p className="text-xs text-gray-400 mt-0.5">{job.company}</p>
                                    </div>
                                    <span className="text-[10px] bg-blue-500/20 text-blue-400 px-2.5 py-0.5 rounded-full font-bold">
                                      {job.duration || "N/A"}
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-500 text-sm">No professional history block detected.</p>
                          )}
                        </div>

                        <div className="border-t border-white/5 pt-5">
                          <h3 className="text-base font-bold mb-3 text-blue-400">Academic History</h3>
                          {analysis?.education && analysis.education.length > 0 ? (
                            <div className="space-y-3">
                              {analysis.education.map((edu, idx) => (
                                <div key={idx} className="bg-slate-900/60 p-4 rounded-xl border border-white/5 flex justify-between items-center text-sm">
                                  <div>
                                    <h4 className="font-bold text-gray-200">{edu.degree}</h4>
                                    <p className="text-xs text-gray-400">{edu.institution}</p>
                                  </div>
                                  <span className="text-xs text-blue-400 font-bold">{edu.year || "N/A"}</span>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-500 text-sm">No academic history detected.</p>
                          )}
                        </div>
                      </div>
                    )}

                    {activeTab === "projects" && (
                      <div className="space-y-6">
                        <div>
                          <h3 className="text-base font-bold mb-3 text-blue-400">Project Highlights</h3>
                          {analysis?.projects && analysis.projects.length > 0 ? (
                            <div className="space-y-3">
                              {analysis.projects.map((proj, idx) => (
                                <div key={idx} className="bg-slate-900/60 p-4 rounded-xl border border-white/5 text-sm space-y-2">
                                  <h4 className="font-bold text-gray-200">{proj.title || proj.name}</h4>
                                  <p className="text-xs text-gray-300">{proj.description}</p>
                                  {proj.technologies && proj.technologies.length > 0 && (
                                    <div className="flex flex-wrap gap-1.5 pt-1">
                                      {proj.technologies.map((tech, tIdx) => (
                                        <span key={tIdx} className="text-[10px] bg-slate-800 text-gray-400 px-2 py-0.5 rounded">
                                          {tech}
                                        </span>
                                      ))}
                                    </div>
                                  )}
                                </div>
                              ))}
                            </div>
                          ) : (
                            <p className="text-gray-500 text-sm">No projects parsed from document.</p>
                          )}
                        </div>

                        <div className="border-t border-white/5 pt-5">
                          <h3 className="text-base font-bold mb-3 text-blue-400">Certifications & Awards</h3>
                          {analysis?.certifications && analysis.certifications.length > 0 ? (
                            <div className="bg-slate-900/60 p-4 rounded-xl border border-white/5 text-sm">
                              <ul className="list-disc pl-5 text-gray-300 space-y-1">
                                {analysis.certifications.map((cert, idx) => (
                                  <li key={idx}>{cert}</li>
                                ))}
                              </ul>
                            </div>
                          ) : (
                            <p className="text-gray-500 text-sm">No certifications parsed.</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* RIGHT SIDE PANEL (PERSISTENT RESUME FILE PREVIEW) */}
          <div className="bg-white/5 backdrop-blur-lg border border-white/10 rounded-3xl p-6 min-h-[600px] w-full">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Resume Preview</h2>
              <span className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded-xl text-sm font-semibold">
                Live Preview
              </span>
            </div>

            <div className="h-[550px] bg-slate-900/70 rounded-2xl flex items-center justify-center border border-white/10 overflow-hidden">
              {file.type === "application/pdf" ? (
                <iframe
                  src={URL.createObjectURL(file)}
                  title="Resume Preview"
                  className="w-full h-full rounded-2xl"
                />
              ) : (
                <div className="text-center p-6">
                  <div className="text-7xl mb-6">📄</div>
                  <h3 className="text-2xl font-semibold mb-3 truncate max-w-[250px] mx-auto">{file.name}</h3>
                  <p className="text-gray-400 text-sm">Preview available only for PDF files</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UploadResume