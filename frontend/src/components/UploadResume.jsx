import { useState } from "react"
import ScoreGauge from "./ScoreGauge"
import { uploadResume } from "../services/api"

function UploadResume() {

  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragging, setDragging] = useState(false)
  const [analysis, setAnalysis] = useState(null)
  const [activeTab, setActiveTab] = useState("overview")

  async function handleUpload(selectedFile) {
    if (!selectedFile) return
    setLoading(true)
    try {
      const response = await uploadResume(selectedFile)
      if (response.error) {
        alert(response.error)
      } else {
        setFile(selectedFile)
        setAnalysis(response)
      }
    } catch (err) {
      alert("Failed to analyze resume. Please try again.")
      console.error(err)
    } finally {
      setLoading(false)
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


  return (

    <div>

      <h1 className="text-5xl font-bold mb-8">
        Upload Resume
      </h1>

      {/* STEP BAR */}
      <div className="flex items-center gap-6 mb-10">

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
            1
          </div>

          <p>Upload</p>

        </div>

        <div className="w-20 h-1 bg-blue-500 rounded" />

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center">
            2
          </div>

          <p>Analyze</p>

        </div>

        <div className="w-20 h-1 bg-slate-700 rounded" />

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center">
            3
          </div>

          <p>Improve</p>

        </div>

      </div>

      {/* BEFORE UPLOAD */}
      {
        !file && !loading && (

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              p-20
              rounded-3xl
              border-2
              border-dashed
              text-center
              transition-all
              duration-300
              cursor-pointer
              max-w-3xl
              mx-auto

              ${dragging
                ? "border-blue-500 bg-blue-500/10 scale-105"
                : "border-white/10 bg-white/5 backdrop-blur-lg"
              }
            `}
          >

            <div className="text-7xl mb-8">
              📄
            </div>

            <h2 className="text-5xl font-bold mb-6">
              Drag & Drop Resume
            </h2>

            <p className="text-gray-400 text-xl mb-8">
              Upload PDF, DOC, or DOCX files
            </p>

            <label
              className="
                inline-block
                bg-blue-500
                hover:bg-blue-600
                px-8
                py-4
                rounded-2xl
                transition
                cursor-pointer
                font-semibold
                text-lg
              "
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

        )
      }

      {/* LOADING */}
      {
        loading && (

          <div
            className="
              mt-10
              bg-white/5
              backdrop-blur-lg
              border
              border-white/10
              p-16
              rounded-3xl
              text-center
              max-w-4xl
              mx-auto
            "
          >

            <div className="space-y-4">

                <div className="h-6 bg-slate-700 rounded animate-pulse" />

                <div className="h-6 bg-slate-700 rounded animate-pulse" />

                <div className="h-32 bg-slate-700 rounded-2xl animate-pulse" />

                </div>

            <h2 className="text-4xl font-bold mt-10 mb-6">
              AI is analyzing your resume
            </h2>

            <p className="text-gray-400 text-lg">
              Extracting skills, calculating ATS score,
              and generating intelligent feedback...
            </p>

          </div>

        )
      }

      {/* AFTER UPLOAD */}
      {
        file && !loading && (

          <div className="grid grid-cols-2 gap-8 mt-10">

            {/* LEFT SIDE */}
            <div>

              {/* AI FEEDBACK */}
              <div
                className="
                  bg-white/5
                  backdrop-blur-lg
                  border
                  border-white/10
                  p-8
                  rounded-3xl
                "
              >

                <div className="flex items-center justify-between mb-6">

                  <h2 className="text-2xl font-bold">
                    AI Resume Feedback
                  </h2>

                  <span
                    className="
                      bg-green-500/20
                      text-green-400
                      px-4
                      py-2
                      rounded-xl
                      text-sm
                    "
                  >
                    Analysis Complete
                  </span>

                </div>

                {/* TABS HEADERS */}
                <div className="flex border-b border-white/10 mb-6 gap-1 overflow-x-auto scrollbar-none">
                  {[
                    { id: "overview", label: "Overview" },
                    { id: "scoring", label: "Scoring breakdown" },
                    { id: "experience", label: "Experience & Edu" },
                    { id: "projects", label: "Projects & Certs" }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`
                        pb-3 px-4 text-sm font-semibold transition-all border-b-2 whitespace-nowrap
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

                {/* TAB CONTENT */}
                {activeTab === "overview" && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                      <div className="bg-slate-900/70 p-6 rounded-2xl border border-white/5">
                        <h3 className="text-sm text-gray-400 font-semibold mb-2">ATS Match Score</h3>
                        <p className="text-5xl font-extrabold text-blue-400">{analysis?.score || 0}%</p>
                      </div>
                      <div className="bg-slate-900/70 p-6 rounded-2xl border border-white/5">
                        <h3 className="text-sm text-gray-400 font-semibold mb-2">Skills Found</h3>
                        <p className="text-sm text-gray-200 line-clamp-3">
                          {analysis?.skills_found && analysis.skills_found.length > 0
                            ? analysis.skills_found.slice(0, 8).join(", ") + (analysis.skills_found.length > 8 ? "..." : "")
                            : "None parsed"}
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex justify-center py-4 bg-slate-900/40 rounded-2xl border border-white/5">
                      <ScoreGauge score={analysis?.score || 0} />
                    </div>

                    {analysis?.detected_strengths && analysis.detected_strengths.length > 0 && (
                      <div className="bg-green-500/10 p-5 rounded-2xl border border-green-500/20">
                        <h4 className="text-green-400 font-bold text-sm mb-3">Detected Strengths</h4>
                        <ul className="space-y-2 text-sm text-gray-300">
                          {analysis.detected_strengths.map((str, idx) => (
                            <li key={idx} className="flex gap-2 items-start">
                              <span>✓</span> <span>{str}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {analysis?.optimization_recommendations && analysis.optimization_recommendations.length > 0 && (
                      <div className="bg-blue-500/10 p-5 rounded-2xl border border-blue-500/20">
                        <h4 className="text-blue-400 font-bold text-sm mb-3">Optimization Tips</h4>
                        <ul className="space-y-2 text-sm text-gray-300">
                          {analysis.optimization_recommendations.map((rec, idx) => (
                            <li key={idx} className="flex gap-2 items-start">
                              <span>•</span> <span>{rec}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "scoring" && (
                  <div className="space-y-6 bg-slate-900/40 p-6 rounded-2xl border border-white/5">
                    <h3 className="text-xl font-bold text-gray-200">ATS Scoring Dimension Breakdown</h3>
                    {analysis?.category_scores ? (
                      <div className="space-y-5">
                        {Object.entries(analysis.category_scores).map(([category, val]) => (
                          <div key={category} className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-300 font-semibold capitalize">{category.replace(/_/g, ' ')}</span>
                              <span className="font-bold text-blue-400">{val}%</span>
                            </div>
                            <div className="w-full bg-slate-900 rounded-full h-3">
                              <div
                                className="bg-blue-500 h-3 rounded-full transition-all duration-700 ease-out"
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
                      <h3 className="text-lg font-bold mb-4 text-blue-400">Professional History</h3>
                      {analysis?.experience && analysis.experience.length > 0 ? (
                        <div className="space-y-4">
                          {analysis.experience.map((job, idx) => (
                            <div key={idx} className="bg-slate-900/60 p-5 rounded-2xl border border-white/5">
                              <div className="flex justify-between items-start mb-3">
                                <div>
                                  <h4 className="font-bold text-gray-100">{job.job_title}</h4>
                                  <p className="text-sm text-gray-400">{job.company}</p>
                                </div>
                                <span className="text-xs bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-medium whitespace-nowrap">
                                  {job.duration || "Duration N/A"}
                                </span>
                              </div>
                              {job.responsibilities && job.responsibilities.length > 0 && (
                                <ul className="list-disc pl-5 text-sm text-gray-300 space-y-1">
                                  {job.responsibilities.map((resp, bIdx) => (
                                    <li key={bIdx}>{resp}</li>
                                  ))}
                                </ul>
                              )}
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-500 text-sm">No professional history block detected.</p>
                      )}
                    </div>

                    <div className="border-t border-white/5 pt-6">
                      <h3 className="text-lg font-bold mb-4 text-blue-400">Academic History</h3>
                      {analysis?.education && analysis.education.length > 0 ? (
                        <div className="space-y-3">
                          {analysis.education.map((edu, idx) => (
                            <div key={idx} className="bg-slate-900/60 p-4 rounded-2xl border border-white/5 flex justify-between items-center">
                              <div>
                                <h4 className="font-bold text-gray-100">{edu.degree}</h4>
                                <p className="text-sm text-gray-400">{edu.institution}</p>
                              </div>
                              <span className="text-sm text-blue-400 font-bold whitespace-nowrap">{edu.year || "Year N/A"}</span>
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
                      <h3 className="text-lg font-bold mb-4 text-blue-400">Project Highlights</h3>
                      {analysis?.projects && analysis.projects.length > 0 ? (
                        <div className="space-y-4">
                          {analysis.projects.map((proj, idx) => (
                            <div key={idx} className="bg-slate-900/60 p-5 rounded-2xl border border-white/5">
                              <h4 className="font-bold text-gray-100 mb-2">{proj.name}</h4>
                              <p className="text-sm text-gray-300 mb-3">{proj.description}</p>
                              {proj.technologies && proj.technologies.length > 0 && (
                                <div className="flex flex-wrap gap-2">
                                  {proj.technologies.map((tech, tIdx) => (
                                    <span key={tIdx} className="text-xs bg-slate-800 text-gray-400 px-2 py-1 rounded">
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

                    <div className="border-t border-white/5 pt-6">
                      <h3 className="text-lg font-bold mb-4 text-blue-400">Certifications & Awards</h3>
                      {analysis?.certifications && analysis.certifications.length > 0 ? (
                        <div className="bg-slate-900/60 p-5 rounded-2xl border border-white/5">
                          <ul className="list-disc pl-5 text-sm text-gray-300 space-y-2">
                            {analysis.certifications.map((cert, idx) => (
                              <li key={idx}>{cert}</li>
                            ))}
                          </ul>
                        </div>
                      ) : (
                        <p className="text-gray-500 text-sm">No certifications parsed from document.</p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* RIGHT SIDE */}
            <div
              className="
                bg-white/5
                backdrop-blur-lg
                border
                border-white/10
                rounded-3xl
                p-6
                min-h-[700px]
              "
            >

              <div className="flex items-center justify-between mb-6">

                <h2 className="text-2xl font-bold">
                  Resume Preview
                </h2>

                <span
                  className="
                    bg-blue-500/20
                    text-blue-400
                    px-4
                    py-2
                    rounded-xl
                    text-sm
                  "
                >
                  Live Preview
                </span>

              </div>

              <div
                className="
                  h-[600px]
                  bg-slate-900/70
                  rounded-2xl
                  flex
                  items-center
                  justify-center
                  border
                  border-white/10
                  overflow-hidden
                "
              >

                {
                  file.type === "application/pdf" ? (

                    <iframe
                      src={URL.createObjectURL(file)}
                      title="Resume Preview"
                      className="
                        w-full
                        h-full
                        rounded-2xl
                      "
                    />

                  ) : (

                    <div className="text-center">

                      <div className="text-7xl mb-6">
                        📄
                      </div>

                      <h3 className="text-2xl font-semibold mb-4">
                        {file.name}
                      </h3>

                      <p className="text-gray-400">
                        Preview available only for PDF files
                      </p>

                    </div>

                  )
                }

              </div>

            </div>

          </div>

        )
      }

    </div>

  )
}

export default UploadResume