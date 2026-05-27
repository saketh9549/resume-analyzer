import { useState, useEffect } from "react"
import { analyzeResume, getAnalysisResults } from "../services/resumeApi"
import { useAnalysisSocket } from "./useAnalysisSocket"

const STAGES = [
  "Uploading file...",
  "Extracting text...",
  "Parsing resume...",
  "Running ATS engine...",
  "Running AI recruiter analysis...",
  "Running semantic matching...",
  "Finalizing recommendations..."
]

export function useAnalysisFlow() {
  const [status, setStatus] = useState("idle") // idle | uploaded | analyzing | completed | failed
  const [currentStageIndex, setCurrentStageIndex] = useState(0)
  const [error, setError] = useState("")
  const [analysisResult, setAnalysisResult] = useState(null)
  const [activeSocketId, setActiveSocketId] = useState(null)

  // Integrate background socket streaming
  const {
    status: wsStatus,
    progress: wsProgress,
    message: wsMessage
  } = useAnalysisSocket(
    activeSocketId,
    // onComplete callback
    async () => {
      try {
        const results = await getAnalysisResults(activeSocketId)
        setAnalysisResult(results)
        setStatus("completed")
        setActiveSocketId(null)
      } catch (err) {
        setStatus("failed")
        setError(err.message || "Failed to retrieve analysis details.")
        setActiveSocketId(null)
      }
    },
    // onError callback
    (errMsg) => {
      setStatus("failed")
      setError(errMsg || "WebSocket processing disconnected.")
      setActiveSocketId(null)
    }
  )

  // Local simulated progress interval for synchronous fallback mode
  useEffect(() => {
    let interval = null
    if (status === "analyzing" && !activeSocketId) {
      setCurrentStageIndex(0)
      interval = setInterval(() => {
        setCurrentStageIndex((prev) => {
          if (prev < STAGES.length - 1) {
            return prev + 1
          }
          return prev
        })
      }, 1000)
    } else {
      setCurrentStageIndex(0)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [status, activeSocketId])

  const runAnalysis = async (resumeId) => {
    if (!resumeId) return
    setStatus("analyzing")
    setError("")
    setAnalysisResult(null)
    try {
      const result = await analyzeResume(resumeId)
      if (result.error) {
        setStatus("failed")
        setError(result.error)
      } else if (result.analysis_status === "queued") {
        // Celery worker kicked off, bind socket connection
        setActiveSocketId(resumeId)
      } else {
        // Inline fallback run completed immediately
        setAnalysisResult(result)
        setStatus("completed")
      }
    } catch (err) {
      setStatus("failed")
      setError(err.message || "Analysis failed due to a server error.")
    }
  }

  const resetFlow = () => {
    setStatus("idle")
    setCurrentStageIndex(0)
    setError("")
    setAnalysisResult(null)
    setActiveSocketId(null)
  }

  return {
    status,
    setStatus,
    currentStage: activeSocketId ? wsMessage : STAGES[currentStageIndex],
    currentStageIndex,
    totalStages: STAGES.length,
    error,
    setError,
    analysisResult,
    runAnalysis,
    resetFlow,
    isBgProcessing: !!activeSocketId,
    bgProgress: wsProgress,
    bgStatus: wsStatus,
    bgMessage: wsMessage
  }
}
