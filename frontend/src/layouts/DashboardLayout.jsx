import { useState } from "react"
import { Outlet } from "react-router-dom"
import Sidebar from "../components/Sidebar"
import Navbar from "../components/Navbar"
import { useTheme } from "../context/ThemeContext"

function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { darkMode } = useTheme()

  return (
    <div
      className={`
        flex
        min-h-screen
        transition-colors
        duration-300
        ${darkMode
          ? "bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white"
          : "bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 text-slate-800"
        }
      `}
    >
      {/* SIDEBAR */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />

      {/* MAIN CONTENT CONTAINER */}
      <div className="flex-1 p-6 md:p-10 overflow-y-auto flex flex-col min-h-screen">
        <Navbar />
        {/* Render nested route sub-views dynamically */}
        <main className="flex-1 mt-4">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout
