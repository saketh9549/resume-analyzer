import React from "react"
import { motion } from "framer-motion"
import { Pin, RefreshCw } from "lucide-react"
import ResumeThumbnail from "./ResumeThumbnail"
import ResumeActionsMenu from "./ResumeActionsMenu"

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
  activeMenuId, 
  setActiveMenuId, 
  isLoading 
}) {
  const scoreVal = parseInt(item.score) || 0

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="bg-slate-950/40 p-5 rounded-2xl border border-white/5 hover:border-white/10 transition-all duration-300 relative group flex flex-col justify-between h-72 shadow-lg hover:shadow-blue-500/5 hover:-translate-y-0.5"
    >
      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-slate-950/85 backdrop-blur-sm z-20 rounded-2xl flex flex-col items-center justify-center space-y-3">
          <RefreshCw className="animate-spin text-blue-400" size={24} />
          <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Processing...</span>
        </div>
      )}

      {/* Thumbnail Header Mock */}
      <ResumeThumbnail score={item.score} category={category} />

      {/* Title & Metadata Line */}
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
        
        {/* Actions Button */}
        <ResumeActionsMenu 
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
          activeMenuId={activeMenuId}
          setActiveMenuId={setActiveMenuId}
        />
      </div>

      {/* Footer (Pin and Match Score) */}
      <div className="flex items-center justify-between border-t border-white/5 pt-3 mt-2 shrink-0">
        {/* Pin & Category Badges */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => onTogglePin(item.id)}
            className={`p-1.5 rounded-lg hover:bg-white/5 transition cursor-pointer ${
              isPinned ? "text-yellow-400" : "text-gray-500 opacity-0 group-hover:opacity-100 focus:opacity-100"
            }`}
            title={isPinned ? "Unpin Resume" : "Pin to Top"}
          >
            <Pin size={12} fill={isPinned ? "currentColor" : "none"} />
          </button>
          <span className="text-[9px] bg-white/5 border border-white/5 text-gray-400 px-2 py-0.5 rounded-md font-bold uppercase tracking-wide">
            {category}
          </span>
        </div>

        {/* ATS score rating */}
        <div className="flex items-center gap-2">
          <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">ATS MATCH</span>
          <span className={`
            px-2.5 py-0.5 rounded-md text-[10px] font-black border
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
      </div>
    </motion.div>
  )
}

export default ResumeCard
