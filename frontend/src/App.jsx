import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom"

import { useState } from "react"

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

function DashboardLayout() {

  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (

    <div
      className="
        flex
        min-h-screen
        bg-gradient-to-br
        from-slate-950
        via-slate-900
        to-slate-950
        text-white
      "
    >

      {/* SIDEBAR */}
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
      />

      {/* MAIN CONTENT */}
      <div className="flex-1 p-10">

        <Navbar />

        <Routes>

          <Route
            path="/"
            element={<Dashboard />}
          />

          <Route
            path="/upload"
            element={<Upload />}
          />

          <Route
            path="/analytics"
            element={<Analytics />}
          />

        </Routes>

      </div>

    </div>
  )
}

function App() {

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
          path="/*"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        />

      </Routes>

    </BrowserRouter>
  )
}

export default App