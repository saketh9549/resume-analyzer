import React from "react"
import { motion } from "framer-motion"
import { Pin, RefreshCw, FileText, Play, Sparkles, AlertCircle } from "lucide-react"
import ResumeThumbnail from "../ResumeThumbnail"
import ResumeStatusBadge from "./ResumeStatusBadge"
import ResumeMenu from "./ResumeMenu"

function ResumeCard({ 
  item, 
  isPinned, 
  category, 
  onTogglePin, 
  onOpenPreview, 
  onAiRewrite, 
  onMockInterview, 
  onVisualAudit, 
  onReScore, 
  onRename, 
  onDownload, 
  onDelete, 
  onCategoryChange, 
  isOpen, 
  onToggle, 
  registerRef,
  onAnalyze,
  isLoading
}) {
  const scoreVal = parseInt(item.score) || 0
  const status = item.analysis_status || (scoreVal > 0 ? "analyzed" : "uploaded")

  // Ensure card has dynamic z-index context if dropdown menu is open
  const cardZIndex = isOpen ? "z-30" : "z-10"

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
      className={`bg-slate-950/40 p-5 rounded-2xl border border-white/5 hover:border-blue-500/20 transition-all duration-300 relative group flex flex-col justify-between h-72 shadow-lg hover:shadow-[0_0_20px_rgba(59,130,246,0.06)] hover:-translate-y-0.5 ${cardZIndex}`}
    >
      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-slate-950/85 backdrop-blur-sm z-20 rounded-2xl flex flex-col items-center justify-center space-y-3">
          <RefreshCw className="animate-spin text-blue-400" size={24} />
          <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Analyzing file...</span>
        </div>
      )}

      {/* Card Header (Thumbnail Mock) */}
      <div className="relative">
        <ResumeThumbnail score={item.score} category={category} />
        
        {/* Pin Badge */}
        <button
          onClick={() => onTogglePin(item.id)}
          className={`absolute top-2 left-2 p-1.5 rounded-lg bg-slate-900/80 border border-white/10 transition cursor-pointer ${
            isPinned ? "text-yellow-400 opacity-100" : "text-gray-500 opacity-0 group-hover:opacity-100 focus:opacity-100"
          }`}
          title={isPinned ? "Unpin Resume" : "Pin to Top"}
        >
          <Pin size={12} fill={isPinned ? "currentColor" : "none"} />
        </button>

        {/* Status Indicator */}
        <div className="absolute top-2 right-2">
          <ResumeStatusBadge status={status} />
        </div>
      </div>

      {/* Info Body */}
      <div className="mt-3 flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h4 
            className="font-bold text-gray-100 truncate group-hover:text-blue-400 transition text-sm" 
            title={item.name}
          >
            {item.name}
          </h4>
          <p className="text-[10px] text-gray-500 mt-0.5">
            Uploaded {item.date}
          </p>
        </div>
        
        {/* Actions Dropdown */}
        <ResumeMenu 
          resumeId={item.id}
          resumeName={item.name}
          onOpenPreview={onOpenPreview}
          onAiRewrite={onAiRewrite}
          onMockInterview={onMockInterview}
          onVisualAudit={onVisualAudit}
          onReScore={onReScore}
          onRename={onRename}
          onDownload={onDownload}
          onDelete={onDelete}
          onCategoryChange={onCategoryChange}
          isOpen={isOpen}
          onToggle={onToggle}
          registerRef={registerRef}
        />
      </div>

      {/* Card Footer (ATS score or Analysis CTA) */}
      <div className="flex items-center justify-between border-t border-white/5 pt-3 mt-2 shrink-0">
        <div className="flex items-center gap-1.5">
          <span className="text-[9px] bg-white/5 border border-white/5 text-gray-400 px-2 py-0.5 rounded-md font-bold uppercase tracking-wide">
            {category}
          </span>
        </div>

        {status === "analyzed" ? (
          <div className="flex items-center gap-2">
            <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">ATS Score</span>
            <span className={`
              px-2.5 py-0.5 rounded-md text-[10px] font-black border
              ${scoreVal >= 80 
                ? "bg-green-500/10 border-green-500/25 text-green-400" 
                : scoreVal >= 60 
                ? "bg-yellow-500/10 border-yellow-500/25 text-yellow-400" 
                : "bg-red-500/10 border-red-500/25 text-red-400"
              }
            `}>
              {scoreVal}%
            </span>
          </div>
        ) : status === "processing" ? (
          <div className="flex items-center gap-2 text-purple-400 animate-pulse">
            <RefreshCw size={12} className="animate-spin" />
            <span className="text-[9px] font-bold uppercase tracking-wider">Running checks...</span>
          </div>
        ) : status === "failed" ? (
          <button
            onClick={() => onAnalyze(item.id)}
            className="flex items-center gap-1.5 bg-rose-500/10 border border-rose-500/20 hover:bg-rose-500/20 text-rose-400 font-bold px-3 py-1.5 rounded-xl transition text-[10px] cursor-pointer"
          >
            <AlertCircle size={10} />
            Retry Analysis
          </button>
        ) : (
          <button
            onClick={() => onAnalyze(item.id)}
            className="flex items-center gap-1 bg-blue-500 hover:bg-blue-600 text-white font-bold px-3.5 py-1.5 rounded-xl transition text-[10px] cursor-pointer shadow-md shadow-blue-500/20"
          >
            <Play size={10} fill="currentColor" />
            Analyze Resume
          </button>
        )}
      </div>
    </motion.div>
  )
}

export default ResumeCard
