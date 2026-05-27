import { useState, useEffect, useRef } from "react"

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

export function useAnalysisSocket(resumeId, onComplete, onError) {
  const [status, setStatus] = useState("idle") // idle | queued | extracting | analyzing | embedding | matching | completed | failed
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState("")
  const socketRef = useRef(null)

  useEffect(() => {
    if (!resumeId) {
      setStatus("idle")
      setProgress(0)
      setMessage("")
      return
    }

    // Dynamic WS url calculation
    const cleanBase = BASE_URL.replace(/\/$/, "")
    const wsUrl = cleanBase.replace(/^http/, "ws") + `/resume/ws/analysis/${resumeId}`
    
    console.log("Connecting to WebSocket:", wsUrl)
    const ws = new WebSocket(wsUrl)
    socketRef.current = ws

    ws.onopen = () => {
      console.log("WebSocket Connection established for:", resumeId)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log("WebSocket event received:", data)
        if (data.status) setStatus(data.status)
        if (data.progress !== undefined) setProgress(data.progress)
        if (data.message) setMessage(data.message)

        if (data.status === "completed" || data.status === "analyzed") {
          if (onComplete) onComplete()
          ws.close()
        } else if (data.status === "failed") {
          if (onError) onError(data.message || "Analysis failed.")
          ws.close()
        }
      } catch (err) {
        console.error("Failed to parse WebSocket message:", err)
      }
    }

    ws.onerror = (err) => {
      console.error("WebSocket error:", err)
      if (onError) onError("WebSocket connection error.")
    }

    ws.onclose = () => {
      console.log("WebSocket Connection closed for:", resumeId)
    }

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close()
      }
    }
  }, [resumeId])

  return {
    status,
    progress,
    message
  }
}
