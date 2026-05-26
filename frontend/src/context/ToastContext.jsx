import { createContext, useContext, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react"

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const showToast = (message, type = "success") => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { id, message, type }])
    
    // Auto remove after 3.5 seconds
    setTimeout(() => {
      removeToast(id)
    }, 3500)
  }

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      
      {/* Toast Render Overlay */}
      <div className="fixed bottom-5 right-5 z-[9999] flex flex-col gap-3 w-80 max-w-[calc(100vw-40px)]">
        <AnimatePresence>
          {toasts.map((toast) => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 30, scale: 0.9 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.85, transition: { duration: 0.2 } }}
              className={`
                flex items-start gap-3 p-4 rounded-2xl border backdrop-blur-xl shadow-2xl transition-all duration-300
                ${toast.type === "success" 
                  ? "bg-green-500/10 border-green-500/25 text-green-400" 
                  : toast.type === "error"
                  ? "bg-red-500/10 border-red-500/25 text-red-400"
                  : "bg-blue-500/10 border-blue-500/25 text-blue-400"
                }
              `}
            >
              {/* Type Icon */}
              <div className="shrink-0 mt-0.5">
                {toast.type === "success" && <CheckCircle2 size={18} />}
                {toast.type === "error" && <AlertCircle size={18} />}
                {toast.type === "info" && <Info size={18} />}
              </div>

              {/* Message */}
              <p className="text-xs font-semibold leading-relaxed flex-1">
                {toast.message}
              </p>

              {/* Close Button */}
              <button
                onClick={() => removeToast(toast.id)}
                className="shrink-0 p-0.5 rounded hover:bg-white/5 transition-colors cursor-pointer text-current opacity-70 hover:opacity-100"
              >
                <X size={14} />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider")
  }
  return context
}
