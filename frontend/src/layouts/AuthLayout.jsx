import { Outlet, Navigate } from "react-router-dom"
import { useTheme } from "../context/ThemeContext"

function AuthLayout() {
  const { darkMode } = useTheme()
  const token = localStorage.getItem("token")

  // If already authenticated, redirect immediately to dashboard
  if (token) {
    return <Navigate to="/" replace />
  }

  return (
    <div
      className={`
        flex
        items-center
        justify-center
        min-h-screen
        w-full
        px-4
        transition-colors
        duration-300
        ${darkMode
          ? "bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white"
          : "bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 text-slate-800"
        }
      `}
    >
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[20%] left-[10%] w-72 h-72 rounded-full bg-blue-500/10 blur-[120px]" />
        <div className="absolute bottom-[20%] right-[10%] w-96 h-96 rounded-full bg-purple-500/10 blur-[150px]" />
      </div>

      <div className="w-full max-w-md relative z-10">
        <Outlet />
      </div>
    </div>
  )
}

export default AuthLayout
