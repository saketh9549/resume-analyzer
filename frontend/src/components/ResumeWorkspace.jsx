import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { useToast } from "../context/ToastContext"
import { useNavigate } from "react-router-dom"
import { 
  listResumes, 
  deleteResume, 
  renameResume, 
  downloadResumeFile, 
  getPreviewUrl 
} from "../services/resumeApi"
import { 
  reanalyzeResume, 
  multimodalAnalyzeResume,
  analyzeResume
} from "../services/api"
import { 
  Search, 
  Filter, 
  Folder, 
  RefreshCw, 
  ChevronDown, 
  Sparkles, 
  X
} from "lucide-react"

import WorkspaceGrid from "./workspace/WorkspaceGrid"
import ResumePreviewModal from "./ResumePreviewModal"

function ResumeWorkspace() {
  const { showToast } = useToast()
  const navigate = useNavigate()
  
  const [uploads, setUploads] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Search, Filter & Sort states
  const [searchQuery, setSearchQuery] = useState("")
  const [scoreFilter, setScoreFilter] = useState("all") // all | high (>=80) | mid (60-79) | low (<60)
  const [sortBy, setSortBy] = useState("date") // date | score | name
  const [selectedCategory, setSelectedCategory] = useState("All")
  
  // LocalStorage state mappings
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

  // Action states
  const [activeMenuId, setActiveMenuId] = useState(null)
  const [actionLoadingId, setActionLoadingId] = useState(null)
  
  // Preview Modal states
  const [previewFileUrl, setPreviewFileUrl] = useState(null)
  const [previewFileName, setPreviewFileName] = useState("")
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  
  // Vision Modal states
  const [visionAnalysis, setVisionAnalysis] = useState(null)
  const [visionLoading, setVisionLoading] = useState(false)

  const CATEGORIES = ["All", "Software", "Product Management", "Marketing", "Others"]

  const fetchResumes = async () => {
    setLoading(true)
    try {
      const data = await listResumes()
      setUploads(data || [])
    } catch (err) {
      console.error("Error fetching resumes:", err)
      showToast("Failed to load uploaded resumes from database.", "error")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchResumes()
  }, [])

  // Pin Toggle
  const handleTogglePin = (id) => {
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

  // Category Change
  const handleCategoryChange = (id, cat) => {
    const updated = { ...categories, [id]: cat }
    setCategories(updated)
    localStorage.setItem("resumeCategories", JSON.stringify(updated))
    showToast(`Categorized as ${cat}.`, "success")
  }

  // Delete Action
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this resume? This will wipe all files from database storage.")) return
    setActionLoadingId(id)
    try {
      await deleteResume(id)
      showToast("Resume and analysis logs deleted successfully from database storage.", "success")
      setUploads(prev => prev.filter(u => u.id !== id))
    } catch (err) {
      showToast(err.message || "Failed to delete resume.", "error")
    } finally {
      setActionLoadingId(null)
    }
  }

  // Rename Action
  const handleRename = async (id, currentName) => {
    const newName = window.prompt("Enter new file name:", currentName)
    if (!newName || !newName.trim() || newName === currentName) return
    setActionLoadingId(id)
    try {
      await renameResume(id, newName.trim())
      showToast("Resume renamed successfully in database.", "success")
      setUploads(prev => prev.map(u => u.id === id ? { ...u, name: newName.trim() } : u))
    } catch (err) {
      showToast(err.message || "Failed to rename resume.", "error")
    } finally {
      setActionLoadingId(null)
    }
  }

  // Download Action
  const handleDownload = async (id, name) => {
    showToast("Streaming file from database storage...", "info")
    try {
      await downloadResumeFile(id, name)
      showToast("Download completed!", "success")
    } catch (err) {
      showToast("Download failed. File might not exist in database.", "error")
    }
  }

  // Re-scoring Action
  const handleReScore = async (id) => {
    setActionLoadingId(id)
    showToast("Launching text re-extraction and database re-scoring...", "info")
    try {
      const res = await reanalyzeResume(id)
      if (res.error) {
        showToast(res.error, "error")
      } else {
        showToast("ATS re-scoring completed successfully!", "success")
        fetchResumes()
      }
    } catch (err) {
      showToast("Failed to re-score resume.", "error")
    } finally {
      setActionLoadingId(null)
    }
  }

  // Unified Analysis Action
  const handleAnalyze = async (id) => {
    setActionLoadingId(id)
    showToast("Launching AI recruiter parsing & ATS diagnostics...", "info")
    try {
      const res = await analyzeResume(id)
      if (res.error) {
        showToast(res.error, "error")
      } else {
        showToast("Resume analysis completed successfully!", "success")
        fetchResumes()
      }
    } catch (err) {
      showToast("Failed to analyze resume.", "error")
    } finally {
      setActionLoadingId(null)
    }
  }

  // Multimodal Vision layout analysis
  const handleVisualAudit = async (id) => {
    setVisionLoading(true)
    setVisionAnalysis(null)
    showToast("Converting PDF to temporary images & running Gemini Vision layout audit...", "info")
    try {
      const res = await multimodalAnalyzeResume(id)
      if (res.error) {
        showToast(res.error, "error")
      } else {
        setVisionAnalysis(res)
        showToast("Visual layout audit completed!", "success")
      }
    } catch (err) {
      showToast("Vision model review failed.", "error")
    } finally {
      setVisionLoading(false)
    }
  }

  // Open Preview Modal
  const handleOpenPreview = (id, name) => {
    const previewUrl = getPreviewUrl(id)
    setPreviewFileUrl(previewUrl)
    setPreviewFileName(name)
    setIsPreviewOpen(true)
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
            Resumes are stored securely in database storage. Previews and downloads stream directly from DB.
          </p>
        </div>
        <button
          onClick={() => navigate("/upload")}
          className="bg-blue-500 hover:bg-blue-600 px-5 py-3 rounded-2xl transition font-semibold text-sm cursor-pointer shadow-lg shadow-blue-500/20"
        >
          Upload New Resume
        </button>
      </div>

      {/* Workspace Grid Layout */}
      {loading ? (
        <div className="flex justify-center items-center py-20">
          <RefreshCw className="animate-spin text-blue-400" size={32} />
        </div>
      ) : (
        <WorkspaceGrid
          uploads={uploads}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          scoreFilter={scoreFilter}
          setScoreFilter={setScoreFilter}
          sortBy={sortBy}
          setSortBy={setSortBy}
          selectedCategory={selectedCategory}
          setSelectedCategory={setSelectedCategory}
          pinnedIds={pinnedIds}
          categories={categories}
          onTogglePin={handleTogglePin}
          onCategoryChange={handleCategoryChange}
          onOpenPreview={handleOpenPreview}
          onAiRewrite={(id) => {
            localStorage.setItem("selectedResumeId", id)
            navigate("/rewriter")
          }}
          onMockInterview={(id) => {
            localStorage.setItem("selectedResumeId", id)
            navigate("/interviews")
          }}
          onVisualAudit={handleVisualAudit}
          onReScore={handleReScore}
          onRename={handleRename}
          onDownload={handleDownload}
          onDelete={handleDelete}
          onAnalyze={handleAnalyze}
          actionLoadingId={actionLoadingId}
        />
      )}

      {/* 1. PDF PREVIEW MODAL */}
      <AnimatePresence>
        {isPreviewOpen && (
          <ResumePreviewModal 
            isOpen={isPreviewOpen}
            onClose={() => setIsPreviewOpen(false)}
            fileUrl={previewFileUrl}
            fileName={previewFileName}
            onDownload={() => handleDownload(uploads.find(u => u.name === previewFileName)?.id, previewFileName)}
          />
        )}
      </AnimatePresence>

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

export default ResumeWorkspace
