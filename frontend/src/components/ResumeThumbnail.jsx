import React from "react"
import { FileText, Award } from "lucide-react"

function ResumeThumbnail({ score, category }) {
  const scoreVal = parseInt(score) || 0
  
  // Dynamic color selection based on score
  const getThemeColor = () => {
    if (scoreVal >= 80) return "text-green-400 border-green-500/30 bg-green-500/5 shadow-green-500/10"
    if (scoreVal >= 60) return "text-yellow-400 border-yellow-500/30 bg-yellow-500/5 shadow-yellow-500/10"
    return "text-red-400 border-red-500/30 bg-red-500/5 shadow-red-500/10"
  }

  const getProgressColor = () => {
    if (scoreVal >= 80) return "bg-green-500"
    if (scoreVal >= 60) return "bg-yellow-500"
    return "bg-red-500"
  }

  return (
    <div className="h-32 bg-slate-950/60 rounded-xl border border-white/5 relative overflow-hidden group-hover:border-white/10 transition-all duration-300 flex items-center justify-center shrink-0">
      {/* Decorative layout skeleton mimicking a resume page */}
      <div className="absolute inset-4 flex flex-col justify-between opacity-25 group-hover:opacity-40 transition-opacity duration-300 pointer-events-none">
        {/* Header section skeleton */}
        <div className="space-y-1">
          <div className="w-16 h-2 bg-white/50 rounded" />
          <div className="w-24 h-1.5 bg-white/30 rounded" />
        </div>
        
        {/* Divider */}
        <div className="w-full h-[1px] bg-white/10" />

        {/* Work experience items skeleton */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center">
            <div className="w-12 h-1.5 bg-white/40 rounded" />
            <div className="w-8 h-1 bg-white/20 rounded" />
          </div>
          <div className="w-full h-1 bg-white/20 rounded" />
          <div className="w-5/6 h-1 bg-white/20 rounded" />
        </div>

        {/* Projects skeleton */}
        <div className="space-y-1">
          <div className="w-14 h-1.5 bg-white/40 rounded" />
          <div className="w-11/12 h-1 bg-white/20 rounded" />
        </div>
      </div>

      {/* Floating Score Emblem */}
      <div className={`z-10 flex flex-col items-center gap-1 border px-3 py-2 rounded-2xl backdrop-blur-md shadow-lg ${getThemeColor()}`}>
        <Award size={18} className="animate-pulse" />
        <span className="text-sm font-black font-mono leading-none">{scoreVal}%</span>
        <span className="text-[8px] font-bold text-gray-400 uppercase tracking-wider">ATS Score</span>
      </div>

      {/* Miniature progress bar at bottom of thumbnail */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-white/5">
        <div 
          className={`h-full ${getProgressColor()} transition-all duration-500`}
          style={{ width: `${scoreVal}%` }}
        />
      </div>
    </div>
  )
}

export default ResumeThumbnail
