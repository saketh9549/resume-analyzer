import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet
} from "react-router-dom"

import { useState, useEffect } from "react"

import Sidebar from "./components/Sidebar"
import Navbar from "./components/Navbar"

import Dashboard from "./pages/Dashboard"
import Upload from "./pages/Upload"
import Analytics from "./pages/Analytics"

import Login from "./pages/Login"
import Signup from "./pages/Signup"

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token")

  if (!token) {
    return <Navigate to="/login" />
  }

  return children
}

function DashboardLayout({ darkMode, setDarkMode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

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

      {/* MAIN CONTENT */}
      <div className="flex-1 p-10 overflow-y-auto">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
        {/* Render child pages dynamically */}
        <Outlet />
      </div>
    </div>
  )
}

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode")
    return saved !== "false" // Default to dark mode (true) if not set
  })

  useEffect(() => {
    localStorage.setItem("darkMode", darkMode)
    if (darkMode) {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [darkMode])

  return (
    <BrowserRouter>
      <Routes>
        {/* AUTH ROUTES */}
        <Route
          path="/login"
          element={<Login />}
        />
        <Route
          path="/signup"
          element={<Signup />}
        />

        {/* PROTECTED APP */}
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout darkMode={darkMode} setDarkMode={setDarkMode} />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/analytics" element={<Analytics />} />
        </Route>

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App