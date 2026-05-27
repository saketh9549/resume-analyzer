import React from "react"
import { RefreshCw, CheckCircle, AlertTriangle, CloudUpload } from "lucide-react"

function ResumeStatusBadge({ status }) {
  const normalizedStatus = (status || "uploaded").toLowerCase()

  switch (normalizedStatus) {
    case "uploaded":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-blue-500/10 border border-blue-500/20 text-blue-400 shadow-sm animate-pulse">
          <CloudUpload size={12} />
          Ready to Analyze
        </span>
      )
    case "processing":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-purple-500/10 border border-purple-500/20 text-purple-400 shadow-sm">
          <RefreshCw size={12} className="animate-spin" />
          Analyzing...
        </span>
      )
    case "analyzed":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 shadow-sm">
          <CheckCircle size={12} />
          Analyzed
        </span>
      )
    case "failed":
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-500/10 border border-rose-500/20 text-rose-400 shadow-sm animate-bounce">
          <AlertTriangle size={12} />
          Failed
        </span>
      )
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-bold bg-gray-500/10 border border-gray-500/20 text-gray-400">
          Unknown
        </span>
      )
  }
}

export default ResumeStatusBadge
