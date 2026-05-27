import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { getRecentUploads, rewriteResumeSection } from "../services/api"
import { Sparkles, RefreshCw, FileText, CheckCircle2, ChevronRight, AlertCircle, Copy, Check } from "lucide-react"
import { useToast } from "../context/ToastContext"

function ResumeRewriter() {
  const [resumes, setResumes] = useState([])
  const [selectedResumeId, setSelectedResumeId] = useState("")
  const [loadingResumes, setLoadingResumes] = useState(true)
  const { showToast } = useToast()

  // Form states
  const [section, setSection] = useState("summary")
  const [originalText, setOriginalText] = useState("")
  const [focusArea, setFocusArea] = useState("ATS Optimization")
  const [loadingRewrite, setLoadingRewrite] = useState(false)
  const [rewriteResult, setRewriteResult] = useState(null)
  
  // UX states
  const [copied, setCopied] = useState(false)
  const [applied, setApplied] = useState(false)

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
          }
        }
      } catch (err) {
        console.error(err)
        showToast("An unexpected error occurred while loading resumes.", "error")
      } finally {
        setLoadingResumes(false)
      }
    }
    loadResumes()
  }, [])

  const handleRunRewrite = async (e) => {
    e.preventDefault()
    if (!selectedResumeId || !originalText.trim()) return
    setLoadingRewrite(true)
    setRewriteResult(null)
    setApplied(false)
    try {
      const res = await rewriteResumeSection(selectedResumeId, section, originalText, focusArea)
      if (res && !res.error) {
        setRewriteResult(res)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingRewrite(false)
    }
  }

  const handleCopyText = () => {
    if (!rewriteResult) return
    navigator.clipboard.writeText(rewriteResult.suggested_text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleApplyText = () => {
    if (!rewriteResult) return
    setOriginalText(rewriteResult.suggested_text)
    setApplied(true)
    setTimeout(() => setApplied(false), 3000)
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Title */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AI Resume Rewriter
          </h1>
          <p className="text-gray-400 mt-2 text-lg">
            ATS-optimize your experience statements and summaries using recruiter-grade wording.
          </p>
        </div>

        {/* Dropdown Selector */}
        {!loadingResumes && resumes.length > 0 && (
          <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-3 rounded-2xl backdrop-blur-md">
            <FileText size={18} className="text-blue-400" />
            <select
              value={selectedResumeId}
              onChange={(e) => setSelectedResumeId(e.target.value)}
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
            Please upload a resume first to run the AI rewriting helpers.
          </p>
          <a
            href="/upload"
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 font-semibold rounded-2xl text-white transition-all shadow-lg shadow-blue-500/20"
          >
            Go to Upload <ChevronRight size={16} />
          </a>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          {/* Editor Input Box */}
          <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6">
            <h3 className="text-2xl font-bold text-gray-200">Section Editor</h3>
            
            <form onSubmit={handleRunRewrite} className="space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-400 font-bold uppercase tracking-wider mb-2">Resume Section</label>
                  <select
                    value={section}
                    onChange={(e) => setSection(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-4 py-3 focus:border-blue-500 transition text-sm font-semibold"
                  >
                    <option value="summary">Professional Summary</option>
                    <option value="experience">Experience bullets</option>
                    <option value="projects">Project descriptions</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs text-gray-400 font-bold uppercase tracking-wider mb-2">Rewrite Focus</label>
                  <select
                    value={focusArea}
                    onChange={(e) => setFocusArea(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-4 py-3 focus:border-blue-500 transition text-sm font-semibold"
                  >
                    <option value="ATS Optimization">ATS Keyword Density</option>
                    <option value="Action Verbs">Action Wording</option>
                    <option value="Technical Metrics">Quantified Impact Metrics</option>
                    <option value="Executive Tone">Executive Leadership</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs text-gray-400 font-bold uppercase tracking-wider mb-2">Original Text</label>
                <textarea
                  value={originalText}
                  onChange={(e) => setOriginalText(e.target.value)}
                  rows={8}
                  required
                  placeholder="Paste the current text block you want the AI to rewrite..."
                  className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-4 focus:border-blue-500 transition text-sm leading-relaxed"
                />
              </div>

              <button
                type="submit"
                disabled={loadingRewrite}
                className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:cursor-not-allowed font-semibold rounded-2xl text-white transition shadow-lg shadow-blue-500/20 cursor-pointer"
              >
                {loadingRewrite ? (
                  <>
                    <RefreshCw className="animate-spin" size={16} /> Generating AI Suggestion...
                  </>
                ) : (
                  <>
                    <Sparkles size={16} /> Rewrite Section with Gemini
                  </>
                )}
              </button>
            </form>
          </div>

          {/* AI Suggestion comparison box */}
          <div className="space-y-6">
            {!rewriteResult && !loadingRewrite ? (
              <div className="bg-white/5 border border-white/10 border-dashed p-16 rounded-3xl text-center text-gray-400 text-sm backdrop-blur-md h-[460px] flex flex-col justify-center items-center">
                <Sparkles size={40} className="mb-4 text-gray-500" />
                Fill in the editor and click rewrite to view comparative suggestions.
              </div>
            ) : loadingRewrite ? (
              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md h-[460px] flex flex-col justify-between animate-pulse">
                <div className="space-y-4">
                  <div className="h-6 w-32 bg-white/10 rounded-full" />
                  <div className="space-y-2">
                    <div className="h-4 w-full bg-white/5 rounded" />
                    <div className="h-4 w-full bg-white/5 rounded" />
                    <div className="h-4 w-3/4 bg-white/5 rounded" />
                  </div>
                </div>
                <div className="h-12 w-full bg-white/5 rounded-2xl" />
              </div>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6"
              >
                <div className="flex justify-between items-center border-b border-white/5 pb-4">
                  <h4 className="font-bold text-xl text-gray-200">AI Suggested Wording</h4>
                  <div className="flex gap-2">
                    <button
                      onClick={handleCopyText}
                      className="p-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 border border-white/10 transition cursor-pointer"
                      title="Copy to Clipboard"
                    >
                      {copied ? <Check size={16} className="text-green-400" /> : <Copy size={16} />}
                    </button>
                  </div>
                </div>

                <div className="p-5 bg-blue-500/5 border border-blue-500/10 rounded-2xl text-sm leading-relaxed text-gray-200 font-medium">
                  {rewriteResult.suggested_text}
                </div>

                {/* Key improvements */}
                <div className="space-y-3">
                  <span className="text-xs text-purple-400 font-bold uppercase tracking-wider block">Key AI Optimizations</span>
                  <div className="space-y-2">
                    {rewriteResult.key_improvements?.map((imp, idx) => (
                      <div key={idx} className="flex gap-2.5 text-xs text-gray-400 items-start">
                        <CheckCircle2 size={14} className="text-green-500 shrink-0 mt-0.5" />
                        <span>{imp}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 flex gap-4">
                  <button
                    onClick={handleApplyText}
                    className="flex-1 py-3.5 rounded-2xl bg-blue-500 hover:bg-blue-600 font-semibold transition text-white text-center cursor-pointer shadow-lg shadow-blue-500/20"
                  >
                    {applied ? "Applied!" : "Apply suggestion to Editor"}
                  </button>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ResumeRewriter
