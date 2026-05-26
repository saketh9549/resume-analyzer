import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useToast } from "../context/ToastContext"
import { useNavigate } from "react-router-dom"
import { 
  getRecentUploads, 
  deleteResume, 
  renameResume, 
  downloadResume, 
  reanalyzeResume,
  multimodalAnalyzeResume 
} from "../services/api"
import { 
  Search, 
  Filter, 
  MoreVertical, 
  FileText, 
  Trash2, 
  Edit3, 
  Download, 
  RefreshCw, 
  Play, 
  Eye, 
  Pin, 
  Folder, 
  Briefcase, 
  ChevronDown, 
  Sparkles, 
  X,
  Gauge
} from "lucide-react"

function RecentUploads() {
  const { showToast } = useToast()
  const navigate = useNavigate()
  
  const [uploads, setUploads] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Search, Filter & Sort states
  const [searchQuery, setSearchQuery] = useState("")
  const [scoreFilter, setScoreFilter] = useState("all") // all | high (>80) | mid (60-80) | low (<60)
  const [sortBy, setSortBy] = useState("date") // date | score | name
  const [selectedCategory, setSelectedCategory] = useState("All")
  
  // Resume state lists
  const [pinnedIds, setPinnedIds] = useState(() => {
    try {
      const saved = localStorage.getItem("pinnedResumes")
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })
  
  const [categories, setCategories] = useState(() => {
    try {
      const saved = localStorage.getItem("resumeCategories")
      return saved ? JSON.parse(saved) : {}
    } catch {
      return {}
    }
  })

  // Action/Menu states
  const [activeMenuId, setActiveMenuId] = useState(null)
  const [actionLoadingId, setActionLoadingId] = useState(null)
  
  // Modals states
  const [previewFileUrl, setPreviewFileUrl] = useState(null)
  const [previewFileName, setPreviewFileName] = useState("")
  
  const [visionAnalysis, setVisionAnalysis] = useState(null)
  const [visionLoading, setVisionLoading] = useState(false)

  // Categories list
  const CATEGORIES = ["All", "Software", "Product Management", "Marketing", "Others"]

  const fetchUploads = async () => {
    setLoading(true)
    try {
      const data = await getRecentUploads()
      setUploads(data || [])
    } catch (err) {
      console.error("Error fetching uploads:", err)
      showToast("Failed to load uploaded resumes.", "error")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUploads()
  }, [])

  // Handle Pin toggle
  const togglePin = (id) => {
    let updatedPins
    if (pinnedIds.includes(id)) {
      updatedPins = pinnedIds.filter(pId => pId !== id)
      showToast("Resume unpinned.", "info")
    } else {
      updatedPins = [...pinnedIds, id]
      showToast("Resume pinned to top.", "success")
    }
    setPinnedIds(updatedPins)
    localStorage.setItem("pinnedResumes", JSON.stringify(updatedPins))
  }

  // Handle Category change
  const setResumeCategory = (id, cat) => {
    const updated = { ...categories, [id]: cat }
    setCategories(updated)
    localStorage.setItem("resumeCategories", JSON.stringify(updated))
    showToast(`Categorized as ${cat}.`, "success")
    setActiveMenuId(null)
  }

  // Action: Delete
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this resume? This cannot be undone.")) return
    setActionLoadingId(id)
    try {
      const res = await deleteResume(id)
      if (res.error) {
        showToast(res.error, "error")
      } else {
        showToast("Resume and analysis logs deleted successfully.", "success")
        setUploads(prev => prev.filter(u => u.id !== id))
      }
    } catch (err) {
      showToast("Failed to delete resume.", "error")
    } finally {
      setActionLoadingId(null)
      setActiveMenuId(null)
    }
  }

  // Action: Rename
  const handleRename = async (id, currentName) => {
    const newName = window.prompt("Enter new file name:", currentName)
    if (!newName || !newName.trim() || newName === currentName) return
    setActionLoadingId(id)
    try {
      const res = await renameResume(id, newName.trim())
      if (res.error) {
        showToast(res.error, "error")
      } else {
        showToast("Resume renamed successfully.", "success")
        setUploads(prev => prev.map(u => u.id === id ? { ...u, name: newName.trim() } : u))
      }
    } catch (err) {
      showToast("Failed to rename resume.", "error")
    } finally {
      setActionLoadingId(null)
      setActiveMenuId(null)
    }
  }

  // Action: Download
  const handleDownload = async (id, name) => {
    showToast("Preparing download...", "info")
    const res = await downloadResume(id, name)
    if (res.error) {
      showToast("Download failed. File might not exist on the server.", "error")
    } else {
      showToast("File downloaded successfully.", "success")
    }
    setActiveMenuId(null)
  }

  // Action: Reanalyze
  const handleReanalyze = async (id) => {
    setActionLoadingId(id)
    showToast("Launching text re-extraction and ATS scanning...", "info")
    try {
      const res = await reanalyzeResume(id)
      if (res.error) {
        showToast(res.error, "error")
      } else {
        showToast("ATS re-scoring completed successfully!", "success")
        fetchUploads()
      }
    } catch (err) {
      showToast("Failed to reanalyze resume.", "error")
    } finally {
      setActionLoadingId(null)
      setActiveMenuId(null)
    }
  }

  // Action: Multimodal Layout Analysis
  const handleMultimodalAnalysis = async (id, filename) => {
    setVisionLoading(true)
    setVisionAnalysis(null)
    showToast("Converting PDF pages to images & launching Gemini Vision Layout analysis...", "info")
    try {
      const res = await multimodalAnalyzeResume(id)
      if (res.error) {
        showToast(res.error, "error")
      } else {
        setVisionAnalysis(res)
        showToast("Layout and visual audit completed!", "success")
      }
    } catch (err) {
      showToast("Vision model review failed.", "error")
    } finally {
      setVisionLoading(false)
      setActiveMenuId(null)
    }
  }

  // Action: Open Preview
  const handleOpenPreview = (id, name) => {
    // Construct preview URL from backend download endpoint
    const token = localStorage.getItem("token")
    const apiBase = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
    const fileUrl = `${apiBase}/resume/${id}/download?token=${token || ""}`
    setPreviewFileUrl(fileUrl)
    setPreviewFileName(name)
    setActiveMenuId(null)
  }

  // Filtering & Sorting Logic
  const getFilteredUploads = () => {
    return uploads
      .filter(item => {
        // Search filter
        const matchSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase())
        
        // Score filter
        const scoreVal = parseInt(item.score) || 0
        let matchScore = true
        if (scoreFilter === "high") matchScore = scoreVal >= 80
        else if (scoreFilter === "mid") matchScore = scoreVal >= 60 && scoreVal < 80
        else if (scoreFilter === "low") matchScore = scoreVal < 60

        // Category filter
        const category = categories[item.id] || "Others"
        let matchCategory = true
        if (selectedCategory !== "All") {
          matchCategory = category === selectedCategory
        }

        return matchSearch && matchScore && matchCategory
      })
      .sort((a, b) => {
        // Pinned resumes always float to top
        const aPinned = pinnedIds.includes(a.id)
        const bPinned = pinnedIds.includes(b.id)
        if (aPinned && !bPinned) return -1
        if (!aPinned && bPinned) return 1

        // Normal sorting
        if (sortBy === "score") {
          return (parseInt(b.score) || 0) - (parseInt(a.score) || 0)
        } else if (sortBy === "name") {
          return a.name.localeCompare(b.name)
        } else { // date descending
          return new Date(b.date) - new Date(a.date)
        }
      })
  }

  const filteredUploads = getFilteredUploads()

  return (
    <div className="bg-slate-900/60 p-6 md:p-8 rounded-3xl border border-white/5 backdrop-blur-xl mt-8">
      {/* Title Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
        <div>
          <h2 className="text-3xl font-black flex items-center gap-2.5">
            <Folder className="text-blue-500" /> Resume Workspace
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Search, sort, categorized, and run multimodal visual audits on your documents.
          </p>
        </div>
        <button
          onClick={() => navigate("/upload")}
          className="bg-blue-500 hover:bg-blue-600 px-5 py-3 rounded-2xl transition font-semibold text-sm cursor-pointer shadow-lg shadow-blue-500/20"
        >
          Upload New Resume
        </button>
      </div>

      {/* Filters bar */}
      <div className="flex flex-col lg:flex-row gap-4 justify-between items-stretch lg:items-center pb-6 border-b border-white/5 mb-8">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search size={18} className="absolute left-4 top-3.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search resumes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-slate-950 border border-white/10 rounded-2xl pl-12 pr-5 py-3 text-sm text-gray-200 outline-none focus:border-blue-500 transition"
          />
        </div>

        {/* Filters Group */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Score Threshold Filter */}
          <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3.5 py-2.5 rounded-2xl text-xs font-semibold">
            <Filter size={14} className="text-blue-400" />
            <select
              value={scoreFilter}
              onChange={(e) => setScoreFilter(e.target.value)}
              className="bg-transparent text-gray-200 outline-none cursor-pointer"
            >
              <option value="all" className="bg-slate-950">All Scores</option>
              <option value="high" className="bg-slate-950">High (≥80%)</option>
              <option value="mid" className="bg-slate-950">Intermediate (60-79%)</option>
              <option value="low" className="bg-slate-950">Needs Work (&lt;60%)</option>
            </select>
          </div>

          {/* Sort selection */}
          <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3.5 py-2.5 rounded-2xl text-xs font-semibold">
            <ChevronDown size={14} className="text-blue-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-transparent text-gray-200 outline-none cursor-pointer"
            >
              <option value="date" className="bg-slate-950">Sort by Date</option>
              <option value="score" className="bg-slate-950">Sort by ATS Score</option>
              <option value="name" className="bg-slate-950">Sort by Name</option>
            </select>
          </div>
        </div>
      </div>

      {/* Category Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto scrollbar-none mb-8">
        {CATEGORIES.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`
              px-4 py-2 rounded-xl text-xs font-semibold transition whitespace-nowrap cursor-pointer
              ${selectedCategory === cat 
                ? "bg-blue-500/10 border border-blue-500/20 text-blue-400" 
                : "bg-white/5 border border-white/5 text-gray-400 hover:text-gray-200"
              }
            `}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Resume Cards Layout */}
      {loading ? (
        <div className="flex justify-center items-center py-20">
          <RefreshCw className="animate-spin text-blue-400" size={32} />
        </div>
      ) : filteredUploads.length === 0 ? (
        <div className="text-center py-16 text-gray-400 bg-slate-950/30 border border-white/5 rounded-3xl">
          <p className="mb-4 text-base font-medium">No resumes match the selected parameters.</p>
          <button
            onClick={() => {
              setSearchQuery("")
              setScoreFilter("all")
              setSelectedCategory("All")
            }}
            className="text-blue-400 hover:text-blue-300 underline text-sm cursor-pointer"
          >
            Reset query filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredUploads.map((item) => {
              const scoreVal = parseInt(item.score) || 0
              const isPinned = pinnedIds.includes(item.id)
              const category = categories[item.id] || "Others"

              return (
                <motion.div
                  key={item.id}
                  layout
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  className="bg-slate-950/40 p-5 rounded-2xl border border-white/5 hover:border-white/10 transition-all duration-300 relative group flex flex-col justify-between h-52 shadow-lg"
                >
                  {/* Top line (pin and actions) */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => togglePin(item.id)}
                        className={`p-1.5 rounded-lg hover:bg-white/5 transition cursor-pointer ${isPinned ? "text-yellow-400" : "text-gray-500 opacity-0 group-hover:opacity-100"}`}
                        title={isPinned ? "Unpin Resume" : "Pin to Top"}
                      >
                        <Pin size={14} fill={isPinned ? "currentColor" : "none"} />
                      </button>
                      <span className="text-[10px] bg-white/5 border border-white/5 text-gray-400 px-2.5 py-0.5 rounded-full font-bold">
                        {category}
                      </span>
                    </div>

                    {/* Actions drop menu */}
                    <div className="relative">
                      <button
                        onClick={() => setActiveMenuId(activeMenuId === item.id ? null : item.id)}
                        className="p-1.5 rounded-lg hover:bg-white/5 text-gray-400 hover:text-gray-200 transition cursor-pointer"
                      >
                        {actionLoadingId === item.id ? (
                          <RefreshCw className="animate-spin text-blue-400" size={14} />
                        ) : (
                          <MoreVertical size={14} />
                        )}
                      </button>

                      {activeMenuId === item.id && (
                        <div className="absolute right-0 mt-2 w-52 bg-slate-900 border border-white/10 rounded-2xl p-1.5 shadow-2xl z-50 divide-y divide-white/5 text-xs text-gray-300">
                          <div className="py-1">
                            <button
                              onClick={() => handleOpenPreview(item.id, item.name)}
                              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
                            >
                              <Eye size={12} /> Open Preview
                            </button>
                            <button
                              onClick={() => {
                                localStorage.setItem("selectedResumeId", item.id)
                                navigate("/rewriter")
                              }}
                              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
                            >
                              <Edit3 size={12} /> AI Rewrite Section
                            </button>
                            <button
                              onClick={() => {
                                localStorage.setItem("selectedResumeId", item.id)
                                navigate("/interviews")
                              }}
                              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
                            >
                              <Play size={12} /> Launch Mock Interview
                            </button>
                            <button
                              onClick={() => handleMultimodalAnalysis(item.id, item.name)}
                              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 text-purple-400 cursor-pointer"
                            >
                              <Sparkles size={12} /> Visual Layout Audit
                            </button>
                          </div>
                          
                          <div className="py-1">
                            <button
                              onClick={() => handleReanalyze(item.id)}
                              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
                            >
                              <RefreshCw size={12} /> Re-extract & Score
                            </button>
                            <button
                              onClick={() => handleRename(item.id, item.name)}
                              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
                            >
                              <Edit3 size={12} /> Rename File
                            </button>
                            <button
                              onClick={() => handleDownload(item.id, item.name)}
                              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
                            >
                              <Download size={12} /> Download PDF
                            </button>
                          </div>

                          <div className="py-1">
                            <span className="block px-3 py-1 text-[9px] text-gray-500 uppercase font-black tracking-wider">Move to category</span>
                            {CATEGORIES.filter(c => c !== "All").map(catName => (
                              <button
                                key={catName}
                                onClick={() => setResumeCategory(item.id, catName)}
                                className="w-full text-left px-3 py-1.5 hover:bg-blue-500/10 hover:text-blue-400 rounded-xl transition flex items-center gap-2 cursor-pointer"
                              >
                                <Folder size={10} /> {catName}
                              </button>
                            ))}
                          </div>

                          <div className="py-1">
                            <button
                              onClick={() => handleDelete(item.id)}
                              className="w-full text-left px-3 py-2 hover:bg-red-500/10 text-red-400 rounded-xl transition flex items-center gap-2 cursor-pointer"
                            >
                              <Trash2 size={12} /> Delete Resume
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Title & Metadata */}
                  <div className="my-3 space-y-1">
                    <h4 className="font-bold text-gray-100 truncate pr-6 group-hover:text-blue-400 transition" title={item.name}>
                      {item.name}
                    </h4>
                    <p className="text-[11px] text-gray-500">
                      Uploaded {item.date}
                    </p>
                  </div>

                  {/* ATS Score display */}
                  <div className="flex items-center justify-between border-t border-white/5 pt-3">
                    <span className="text-[10px] text-gray-500 font-bold uppercase tracking-wider">ATS MATCH RATING</span>
                    <span className={`
                      px-3 py-1 rounded-full text-xs font-black border
                      ${scoreVal >= 80 
                        ? "bg-green-500/10 border-green-500/25 text-green-400" 
                        : scoreVal >= 60 
                        ? "bg-yellow-500/10 border-yellow-500/25 text-yellow-400" 
                        : "bg-red-500/10 border-red-500/25 text-red-400"
                      }
                    `}>
                      {item.score}
                    </span>
                  </div>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>
      )}

      {/* 1. PDF PREVIEW MODAL */}
      {previewFileUrl && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[9999] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-slate-900 border border-white/10 w-full max-w-4xl h-[85vh] rounded-3xl p-6 flex flex-col justify-between shadow-2xl relative"
          >
            <div className="flex items-center justify-between pb-4 border-b border-white/5">
              <div>
                <h3 className="text-xl font-bold text-gray-200">Resume Live Preview</h3>
                <p className="text-xs text-gray-400 truncate mt-0.5">{previewFileName}</p>
              </div>
              <button
                onClick={() => setPreviewFileUrl(null)}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 transition cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>
            
            <div className="flex-1 my-4 bg-slate-950 rounded-2xl overflow-hidden border border-white/5">
              <iframe
                src={previewFileUrl}
                title="PDF File Preview"
                className="w-full h-full border-none"
              />
            </div>
            
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setPreviewFileUrl(null)}
                className="px-5 py-2.5 bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl transition text-sm font-semibold cursor-pointer"
              >
                Close Preview
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* 2. GEMINI VISION ANALYSIS MODAL */}
      {visionLoading && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[9999] flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-white/10 p-12 rounded-3xl text-center space-y-4 max-w-sm w-full shadow-2xl animate-pulse">
            <Sparkles className="animate-spin text-purple-400 mx-auto" size={40} />
            <h4 className="text-xl font-bold text-gray-200">Running Layout Scan...</h4>
            <p className="text-xs text-gray-400 leading-relaxed">
              Gemini Vision is auditing typographic consistency, grid alignment, white space margins, and visual balance.
            </p>
          </div>
        </div>
      )}

      {visionAnalysis && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[9999] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, y: 15, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            className="bg-slate-900 border border-white/10 w-full max-w-4xl h-[85vh] rounded-3xl p-6 flex flex-col justify-between shadow-2xl overflow-hidden"
          >
            <div className="flex items-center justify-between pb-4 border-b border-white/5 shrink-0">
              <div className="flex items-center gap-2">
                <Sparkles className="text-purple-400 animate-pulse" size={24} />
                <div>
                  <h3 className="text-xl font-extrabold text-gray-200">Multimodal Visual Layout Audit</h3>
                  <p className="text-xs text-gray-400 mt-0.5">Gemini Vision Typographic & Layout Diagnostics</p>
                </div>
              </div>
              <button
                onClick={() => setVisionAnalysis(null)}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 transition cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            {/* Score Grid & Recommendations scrollable */}
            <div className="flex-1 my-6 overflow-y-auto space-y-8 pr-2">
              {/* Score breakdown metrics cards */}
              <div>
                <h4 className="text-xs text-purple-400 font-bold uppercase tracking-wider block mb-4">Layout Score Dimensions</h4>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {[
                    { label: "Layout Quality", score: visionAnalysis.visual_scores?.layout_score },
                    { label: "Design Consistency", score: visionAnalysis.visual_scores?.design_score },
                    { label: "Readability Spacing", score: visionAnalysis.visual_scores?.readability_score },
                    { label: "Formatting Alignment", score: visionAnalysis.visual_scores?.formatting_score },
                    { label: "Visual Balance", score: visionAnalysis.visual_scores?.visual_balance_score },
                    { label: "Recruiter Ease", score: visionAnalysis.visual_scores?.recruiter_readability_score },
                    { label: "ATS Layout Friendliness", score: visionAnalysis.visual_scores?.ats_friendliness_score },
                    { label: "Overall Visual Rating", score: visionAnalysis.visual_scores?.overall_visual_score }
                  ].map((dim, i) => (
                    <div key={i} className="bg-slate-950/60 p-4 rounded-2xl border border-white/5 flex flex-col justify-between h-24">
                      <span className="text-[10px] text-gray-500 font-bold leading-tight uppercase block">{dim.label}</span>
                      <span className="text-3xl font-extrabold text-blue-400 block mt-2">{dim.score || 70}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Text Feedback */}
              <div className="p-5 bg-white/5 border border-white/5 rounded-2xl space-y-2 text-sm leading-relaxed">
                <span className="text-xs text-blue-400 font-bold uppercase tracking-wider block">Visual Audit Summary</span>
                <p className="text-gray-300">
                  {visionAnalysis.layout_feedback}
                </p>
              </div>

              {/* Suggestions bullets lists */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-950/30 border border-white/5 p-5 rounded-2xl space-y-4">
                  <h5 className="font-bold text-sm text-gray-200 border-b border-white/5 pb-2">Design & Typography Suggestions</h5>
                  <ul className="space-y-2.5 text-xs text-gray-400">
                    {visionAnalysis.design_suggestions?.map((item, idx) => (
                      <li key={idx} className="flex gap-2 items-start leading-relaxed">
                        <span className="text-purple-400 font-bold shrink-0 mt-0.5">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-950/30 border border-white/5 p-5 rounded-2xl space-y-4">
                  <h5 className="font-bold text-sm text-gray-200 border-b border-white/5 pb-2">Readability & Spacing Improvements</h5>
                  <ul className="space-y-2.5 text-xs text-gray-400">
                    {visionAnalysis.readability_improvements?.map((item, idx) => (
                      <li key={idx} className="flex gap-2 items-start leading-relaxed">
                        <span className="text-blue-400 font-bold shrink-0 mt-0.5">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-950/30 border border-white/5 p-5 rounded-2xl space-y-4">
                  <h5 className="font-bold text-sm text-gray-200 border-b border-white/5 pb-2">Formatting Consistency Optimizations</h5>
                  <ul className="space-y-2.5 text-xs text-gray-400">
                    {visionAnalysis.formatting_optimizations?.map((item, idx) => (
                      <li key={idx} className="flex gap-2 items-start leading-relaxed">
                        <span className="text-green-400 font-bold shrink-0 mt-0.5">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-950/30 border border-white/5 p-5 rounded-2xl space-y-4">
                  <h5 className="font-bold text-sm text-gray-200 border-b border-white/5 pb-2">Layout & Section Ordering Recommendations</h5>
                  <ul className="space-y-2.5 text-xs text-gray-400">
                    {visionAnalysis.section_ordering_improvements?.map((item, idx) => (
                      <li key={idx} className="flex gap-2 items-start leading-relaxed">
                        <span className="text-yellow-400 font-bold shrink-0 mt-0.5">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-2 border-t border-white/5 pt-4 shrink-0">
              <button
                onClick={() => setVisionAnalysis(null)}
                className="px-5 py-2.5 bg-blue-500 hover:bg-blue-600 rounded-xl transition text-sm font-semibold cursor-pointer text-white"
              >
                Acknowledge Review
              </button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  )
}

export default RecentUploads