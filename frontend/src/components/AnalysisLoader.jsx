import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"

const LOADING_STEPS = [
  "Extracting document text metrics...",
  "Running heuristic segmentation search...",
  "Evaluating technical keywords density...",
  "Calculating ATS Scoring Dimensions...",
  "Generating Google Gemini Recruiter review...",
  "Structuring candidate learning roadmap..."
]

function AnalysisLoader() {
  const [stepIdx, setStepIdx] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setStepIdx((prev) => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev))
    }, 2500) // Change text statement every 2.5 seconds

    return () => clearInterval(interval)
  }, [])

  return (
    <div className="space-y-8 py-10">
      {/* STEPS TYPING TEXT */}
      <div className="text-center space-y-3">
        <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        
        <h3 className="text-xl font-bold text-gray-100">Analyzing Your Resume</h3>
        
        <div className="h-6 relative overflow-hidden max-w-sm mx-auto">
          <AnimatePresence mode="wait">
            <motion.p
              key={stepIdx}
              initial={{ y: 15, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -15, opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="text-gray-400 text-sm font-medium"
            >
              {LOADING_STEPS[stepIdx]}
            </motion.p>
          </AnimatePresence>
        </div>
      </div>

      {/* SHIMMER/SKELETON CARDS */}
      <div className="space-y-4 max-w-2xl mx-auto">
        {[1, 2, 3].map((item) => (
          <div
            key={item}
            className="p-6 bg-white/5 rounded-3xl border border-white/10 space-y-3 animate-pulse"
          >
            <div className="h-4 bg-slate-800 rounded w-1/3" />
            <div className="h-3 bg-slate-800 rounded w-full" />
            <div className="h-3 bg-slate-800 rounded w-5/6" />
          </div>
        ))}
      </div>
    </div>
  )
}

export default AnalysisLoader
