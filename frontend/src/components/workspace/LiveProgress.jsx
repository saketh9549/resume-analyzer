import React from "react"
import { motion } from "framer-motion"
import { 
  Loader2, 
  CheckCircle2, 
  AlertCircle, 
  FileText, 
  Cpu, 
  Award, 
  Binary, 
  Sparkles, 
  Check 
} from "lucide-react"

export default function LiveProgress({ status, progress, message }) {
  // Steps matching the Celery status workflow
  const steps = [
    {
      key: "queued",
      label: "Task Queued",
      description: "Queueing worker threads...",
      icon: Cpu,
      minProgress: 5,
    },
    {
      key: "extracting",
      label: "Text Extraction",
      description: "Extracting structural raw text...",
      icon: FileText,
      minProgress: 15,
    },
    {
      key: "analyzing",
      label: "ATS Scoring Engine",
      description: "Parsing sections and verifying metrics...",
      icon: Award,
      minProgress: 35,
    },
    {
      key: "embedding",
      label: "Semantic Indexing",
      description: "Generating multi-vector text embeddings...",
      icon: Binary,
      minProgress: 70,
    },
    {
      key: "matching",
      label: "Recruiter AI Review",
      description: "Running recruiter audits and design scans...",
      icon: Sparkles,
      minProgress: 85,
    },
  ]

  const getStepState = (step, idx) => {
    if (status === "failed") {
      // If we are on or after the stage that failed (determined by progress)
      if (progress >= step.minProgress && (idx === steps.length - 1 || progress < steps[idx + 1].minProgress)) {
        return "failed"
      }
    }
    
    if (status === "completed" || status === "analyzed") {
      return "completed"
    }

    // Determine current active step by matching the status key or progress range
    const isCurrentStatus = status === step.key
    const isProgressActive = progress >= step.minProgress && (idx === steps.length - 1 || progress < steps[idx + 1].minProgress)
    
    if (isCurrentStatus || isProgressActive) {
      return "active"
    }

    if (progress > step.minProgress) {
      return "completed"
    }

    return "pending"
  }

  return (
    <div className="max-w-xl mx-auto p-8 bg-slate-900/80 border border-white/10 rounded-3xl text-left space-y-8 shadow-2xl backdrop-blur-xl">
      {/* Header Info */}
      <div className="text-center space-y-3">
        <div className="relative w-20 h-20 mx-auto flex items-center justify-center">
          {status === "failed" ? (
            <div className="w-16 h-16 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-full flex items-center justify-center shadow-lg shadow-rose-500/5">
              <AlertCircle size={32} />
            </div>
          ) : status === "completed" || status === "analyzed" ? (
            <div className="w-16 h-16 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center shadow-lg shadow-emerald-500/5 animate-pulse">
              <CheckCircle2 size={32} />
            </div>
          ) : (
            <>
              <Loader2 className="animate-spin text-blue-400 absolute w-full h-full" size={48} />
              <div className="w-12 h-12 bg-blue-500/10 rounded-full flex items-center justify-center">
                <Cpu className="text-blue-400 animate-pulse" size={20} />
              </div>
            </>
          )}
        </div>

        <div className="space-y-1">
          <h3 className="text-xl font-black text-gray-100 tracking-tight">
            {status === "failed" 
              ? "Analysis Interrupted" 
              : status === "completed" || status === "analyzed"
              ? "Intelligence Ready"
              : "Analyzing Resume..."}
          </h3>
          <p className="text-xs text-gray-400 max-w-sm mx-auto font-medium">
            {message || "Initializing pipeline protocols..."}
          </p>
        </div>
      </div>

      {/* Progress slider bar */}
      <div className="space-y-1.5">
        <div className="flex justify-between items-center text-[10px] font-bold text-gray-500 uppercase tracking-widest px-0.5">
          <span>Pipeline Status</span>
          <span className="font-extrabold text-blue-400">{progress}%</span>
        </div>
        <div className="w-full bg-white/5 rounded-full h-2.5 overflow-hidden border border-white/5">
          <motion.div 
            className={`h-full rounded-full bg-gradient-to-r ${
              status === "failed" 
                ? "from-rose-600 to-rose-400" 
                : "from-blue-500 via-indigo-500 to-purple-500"
            }`}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.4, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Step Stepper Timeline */}
      <div className="relative pl-6 border-l border-white/5 space-y-6 mt-4">
        {steps.map((step, idx) => {
          const stepState = getStepState(step, idx)
          const StepIcon = step.icon

          return (
            <div key={step.key} className="relative flex items-start gap-4 group">
              {/* Timeline dot element */}
              <div className="absolute -left-[31px] top-1">
                {stepState === "completed" ? (
                  <div className="w-4 h-4 rounded-full bg-emerald-500 border border-emerald-400 flex items-center justify-center shadow-lg shadow-emerald-500/25">
                    <Check size={9} className="text-slate-950 font-black" />
                  </div>
                ) : stepState === "active" ? (
                  <div className="w-4 h-4 rounded-full bg-blue-500 border border-blue-400 flex items-center justify-center shadow-lg shadow-blue-500/25 animate-ping" />
                ) : stepState === "failed" ? (
                  <div className="w-4 h-4 rounded-full bg-rose-500 border border-rose-400 flex items-center justify-center shadow-lg shadow-rose-500/25">
                    <AlertCircle size={9} className="text-white" />
                  </div>
                ) : (
                  <div className="w-4 h-4 rounded-full bg-slate-950 border border-white/10 group-hover:border-white/20 transition-all duration-300" />
                )}
              </div>

              {/* Step info block */}
              <div className="flex gap-3">
                <div className={`p-2 rounded-xl border shrink-0 transition-colors duration-300 ${
                  stepState === "completed"
                    ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                    : stepState === "active"
                    ? "bg-blue-500/10 border-blue-500/25 text-blue-400"
                    : stepState === "failed"
                    ? "bg-rose-500/10 border-rose-500/20 text-rose-400"
                    : "bg-white/5 border-white/10 text-gray-500"
                }`}>
                  <StepIcon size={16} />
                </div>
                <div>
                  <h4 className={`text-sm font-bold transition-colors duration-300 ${
                    stepState === "completed"
                      ? "text-gray-100"
                      : stepState === "active"
                      ? "text-blue-400"
                      : stepState === "failed"
                      ? "text-rose-400"
                      : "text-gray-500"
                  }`}>
                    {step.label}
                  </h4>
                  <p className={`text-xs mt-0.5 transition-colors duration-300 ${
                    stepState === "active" 
                      ? "text-gray-300" 
                      : stepState === "completed"
                      ? "text-gray-400"
                      : "text-gray-600"
                  }`}>
                    {stepState === "active" && message ? message : step.description}
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
