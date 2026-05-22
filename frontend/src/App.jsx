import { BrowserRouter, Routes, Route } from "react-router-dom"

import Sidebar from "./components/Sidebar"

import Dashboard from "./pages/Dashboard"
import Upload from "./pages/Upload"
import Analytics from "./pages/Analytics"

function App() {
  return (

    <BrowserRouter>

      <div className="flex bg-slate-950 text-white min-h-screen">

        <Sidebar />

        <div className="flex-1 p-10">

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