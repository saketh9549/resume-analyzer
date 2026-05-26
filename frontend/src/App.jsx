import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom"

import { ThemeProvider } from "./context/ThemeContext"
import DashboardLayout from "./layouts/DashboardLayout"
import AuthLayout from "./layouts/AuthLayout"

import Dashboard from "./pages/Dashboard"
import Upload from "./pages/Upload"
import JobMatching from "./pages/JobMatching"
import ResumeRewriter from "./pages/ResumeRewriter"
import InterviewPrep from "./pages/InterviewPrep"
import LiveJobs from "./pages/LiveJobs"
import RecruiterConsole from "./pages/RecruiterConsole"
import Analytics from "./pages/Analytics"
import Profile from "./pages/Profile"
import Settings from "./pages/Settings"

import Login from "./pages/Login"
import Signup from "./pages/Signup"

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
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App