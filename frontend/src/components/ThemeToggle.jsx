import { useTheme } from "../context/ThemeContext"

function ThemeToggle() {
  const { darkMode, toggleTheme } = useTheme()

  return (
    <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/10">
      <div>
        <p className="font-semibold text-lg">Interface Theme</p>
        <p className="text-sm text-gray-400">
          Switch between Light Mode and Dark Mode layouts.
        </p>
      </div>

      <button
        onClick={toggleTheme}
        className={`
          flex items-center gap-3 px-5 py-3 rounded-2xl border transition-all duration-300 font-semibold text-sm
          ${darkMode
            ? "bg-slate-800 border-white/10 hover:bg-slate-700 text-yellow-400"
            : "bg-blue-50 border-blue-200 hover:bg-blue-100 text-blue-600 shadow-sm"
          }
        `}
      >
        <span>{darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}</span>
      </button>
    </div>
  )
}

export default ThemeToggle
