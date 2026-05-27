import React from "react"
import { 
  Eye, 
  Edit3, 
  Play, 
  Sparkles, 
  RefreshCw, 
  Download, 
  Folder, 
  Trash2,
  MoreVertical
} from "lucide-react"

function ResumeMenu({ 
  resumeId, 
  resumeName, 
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
  registerRef 
}) {
  const CATEGORIES = ["Software", "Product Management", "Marketing", "Others"]

  return (
    <div className="relative inline-block" ref={registerRef}>
      <button
        onClick={(e) => {
          e.stopPropagation()
          onToggle()
        }}
        className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-gray-400 hover:text-gray-200 transition cursor-pointer"
        title="Open Actions Menu"
      >
        <MoreVertical size={14} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-52 bg-slate-900 border border-white/10 rounded-2xl p-1.5 shadow-2xl z-50 divide-y divide-white/5 text-xs text-gray-300">
          {/* Main Actions */}
          <div className="py-1">
            <button
              onClick={(e) => { e.stopPropagation(); onOpenPreview(); onToggle(); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
            >
              <Eye size={12} className="text-blue-400" /> Open Preview
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onAiRewrite(); onToggle(); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
            >
              <Edit3 size={12} className="text-emerald-400" /> AI Rewrite Section
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onMockInterview(); onToggle(); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
            >
              <Play size={12} className="text-cyan-400" /> Launch Mock Interview
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onVisualAudit(); onToggle(); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 text-purple-400 cursor-pointer"
            >
              <Sparkles size={12} className="text-purple-400 animate-pulse" /> Visual Layout Audit
            </button>
          </div>
          
          {/* Operations */}
          <div className="py-1">
            <button
              onClick={(e) => { e.stopPropagation(); onReScore(); onToggle(); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
            >
              <RefreshCw size={12} className="text-blue-400" /> Re-extract & Score
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onRename(); onToggle(); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
            >
              <Edit3 size={12} /> Rename File
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onDownload(); onToggle(); }}
              className="w-full text-left px-3 py-2 hover:bg-white/5 rounded-xl transition flex items-center gap-2 cursor-pointer"
            >
              <Download size={12} className="text-blue-400" /> Download PDF
            </button>
          </div>

          {/* Categorize */}
          <div className="py-1">
            <span className="block px-3 py-1 text-[9px] text-gray-500 uppercase font-black tracking-wider">Move to category</span>
            {CATEGORIES.map(catName => (
              <button
                key={catName}
                onClick={(e) => { e.stopPropagation(); onCategoryChange(catName); onToggle(); }}
                className="w-full text-left px-3 py-1.5 hover:bg-blue-500/10 hover:text-blue-400 rounded-xl transition flex items-center gap-2 cursor-pointer"
              >
                <Folder size={10} /> {catName}
              </button>
            ))}
          </div>

          {/* Destructive actions */}
          <div className="py-1">
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(); onToggle(); }}
              className="w-full text-left px-3 py-2 hover:bg-red-500/10 text-red-400 rounded-xl transition flex items-center gap-2 cursor-pointer"
            >
              <Trash2 size={12} /> Delete Resume
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default ResumeMenu
