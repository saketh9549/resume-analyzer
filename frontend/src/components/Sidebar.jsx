import { Link, useLocation } from "react-router-dom"

import {
  LayoutDashboard,
  Upload,
  BarChart3
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
      name: "Analytics",
      path: "/analytics",
      icon: <BarChart3 size={20} />
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
        ${sidebarOpen ? "w-64" : "w-23"}
      `}
    >

      {/* Top */}
      <div className="flex items-center justify-between mb-10">

        {
          sidebarOpen && (
            <h1 className="text-3xl font-bold">
              ResumeAI
            </h1>
          )
        }

        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="
            bg-slate-800
            p-2
            rounded-xl
            hover:bg-slate-700
            transition
          "
        >
            {sidebarOpen ? "👈" : "👉"}
        </button>

      </div>

      {/* Navigation */}
      <ul className="space-y-4">

        {
          navItems.map((item, index) => (

            <li key={index}>

              <Link
                to={item.path}
                className={`
                  flex
                  items-center
                  gap-4
                  p-3
                  rounded-2xl
                  transition-all
                  duration-200
                  hover:bg-white/10
                  hover:translate-x-1

                  ${location.pathname === item.path
                    ? "bg-blue-500 text-white shadow-lg"
                    : "text-gray-300"
                  }
                `}
              >

                {item.icon}

                {
                  sidebarOpen && (
                    <span>{item.name}</span>
                  )
                }

              </Link>

            </li>

          ))
        }

      </ul>

    </div>

  )
}

export default Sidebar