import { Link, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  Upload,
  BarChart3,
  User,
  Settings as SettingsIcon,
  Briefcase,
  Sparkles,
  HelpCircle,
  Globe,
  Users
} from "lucide-react"

function Sidebar({ sidebarOpen, setSidebarOpen }) {
  const location = useLocation()

  const navItems = [
    {
      name: "Dashboard",
      path: "/",
      icon: <LayoutDashboard size={20} />
    },
    {
      name: "Upload",
      path: "/upload",
      icon: <Upload size={20} />
    },
    {
      name: "Job Match",
      path: "/jobs",
      icon: <Briefcase size={20} />
    },
    {
      name: "AI Rewriter",
      path: "/rewriter",
      icon: <Sparkles size={20} />
    },
    {
      name: "Interview Prep",
      path: "/interviews",
      icon: <HelpCircle size={20} />
    },
    {
      name: "Live Jobs",
      path: "/live-jobs",
      icon: <Globe size={20} />
    },
    {
      name: "Recruiter Portal",
      path: "/recruiter",
      icon: <Users size={20} />
    },
    {
      name: "Analytics",
      path: "/analytics",
      icon: <BarChart3 size={20} />
    },
    {
      name: "Profile",
      path: "/profile",
      icon: <User size={20} />
    },
    {
      name: "Settings",
      path: "/settings",
      icon: <SettingsIcon size={20} />
    }
  ]

  return (
    <div
      className={`
        bg-slate-900/80
        backdrop-blur-lg
        border-r
        border-white/10
        p-6
        transition-all
        duration-300
        flex flex-col
        ${sidebarOpen ? "w-64" : "w-20"}
      `}
    >
      {/* Top logo block */}
      <div className="flex items-center justify-between mb-10">
        {sidebarOpen && (
          <h1 className="text-3xl font-black bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            ResumeAI
          </h1>
        )}

        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="
            bg-slate-800
            p-2
            rounded-xl
            hover:bg-slate-700
            transition
            cursor-pointer
            flex items-center justify-center
          "
        >
          {sidebarOpen ? "👈" : "👉"}
        </button>
      </div>

      {/* Navigation List */}
      <ul className="space-y-3 flex-1">
        {navItems.map((item, index) => (
          <li key={index}>
            <Link
              to={item.path}
              className={`
                flex
                items-center
                gap-4
                p-3.5
                rounded-2xl
                transition-all
                duration-200
                hover:bg-white/5
                hover:translate-x-1

                ${location.pathname === item.path
                  ? "bg-blue-500 text-white shadow-lg shadow-blue-500/20 font-semibold"
                  : "text-gray-400 hover:text-gray-200"
                }
              `}
            >
              {item.icon}

              {sidebarOpen && (
                <span className="text-sm">{item.name}</span>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Sidebar