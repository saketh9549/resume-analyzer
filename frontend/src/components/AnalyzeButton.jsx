import { motion } from "framer-motion"

function AnalyzeButton({ onClick, disabled, status }) {
  let buttonText = "Analyze Resume"
  if (status === "analyzing") {
    buttonText = "Analyzing Resume..."
  } else if (status === "completed") {
    buttonText = "Analysis Complete"
  }

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      onClick={onClick}
      disabled={disabled}
      className={`
        w-full md:max-w-md mx-auto flex items-center justify-center gap-3 px-8 py-4.5 rounded-2xl font-bold text-lg transition-all duration-300 shadow-xl
        ${disabled
          ? "bg-slate-800 text-gray-500 border border-white/5 cursor-not-allowed"
          : "bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 hover:from-blue-700 hover:to-purple-700 text-white cursor-pointer hover:shadow-blue-500/10"
        }
      `}
    >
      {status === "analyzing" && (
        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
      )}
      <span>{buttonText}</span>
    </motion.button>
  )
}

export default AnalyzeButton
