import { lazy, Suspense } from "react"
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom"

import { ThemeProvider } from "./context/ThemeContext"
import DashboardLayout from "./layouts/DashboardLayout"
import AuthLayout from "./layouts/AuthLayout"

// Eagerly loaded pages (small, frequently visited)
import Dashboard from "./pages/Dashboard"
import Upload from "./pages/Upload"
import Login from "./pages/Login"
import Signup from "./pages/Signup"

// Lazy-loaded pages (large, less frequently visited) — reduces initial bundle size
const JobMatching = lazy(() => import("./pages/JobMatching"))
const ResumeRewriter = lazy(() => import("./pages/ResumeRewriter"))
const InterviewPrep = lazy(() => import("./pages/InterviewPrep"))
const LiveJobs = lazy(() => import("./pages/LiveJobs"))
const RecruiterConsole = lazy(() => import("./pages/RecruiterConsole"))
const Analytics = lazy(() => import("./pages/Analytics"))
const Profile = lazy(() => import("./pages/Profile"))
const Settings = lazy(() => import("./pages/Settings"))

// Lazy loading fallback component
function LazyFallback() {
  return (
    <div className="flex items-center justify-center h-64">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-gray-400 font-medium">Loading...</span>
      </div>
    </div>
  )
}

// ProtectedRoute authentication guard component
function ProtectedRoute({ children }) {
  const token = localStorage.getItem("token")

  if (!token) {
    return <Navigate to="/login" replace />
  }

  return children
}

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Suspense fallback={<LazyFallback />}>
          <Routes>
            {/* AUTHENTICATION WRAPPER ROUTE GROUP */}
            <Route element={<AuthLayout />}>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
            </Route>

            {/* PROTECTED DASHBOARD CORE ROUTES */}
            <Route
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/jobs" element={<JobMatching />} />
              <Route path="/rewriter" element={<ResumeRewriter />} />
              <Route path="/interviews" element={<InterviewPrep />} />
              <Route path="/live-jobs" element={<LiveJobs />} />
              <Route path="/recruiter" element={<RecruiterConsole />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/settings" element={<Settings />} />
            </Route>

            {/* Fallback route redirecting back to main landing index */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App