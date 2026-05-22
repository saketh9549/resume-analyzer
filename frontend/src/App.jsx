import { useState } from "react"

import { BrowserRouter, Routes, Route } from "react-router-dom"
import Sidebar from "./components/Sidebar"
import Navbar from "./components/Navbar"
import Dashboard from "./pages/Dashboard"
import Upload from "./pages/Upload"
import Analytics from "./pages/Analytics"

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  return (

    <BrowserRouter>
      
      <div className="flex bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white min-h-screen">

        <Sidebar
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
        />

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

    </BrowserRouter>

  )
}

export default App