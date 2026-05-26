import { useState } from "react"
import { motion } from "framer-motion"
import SettingsCard from "../components/SettingsCard"
import ThemeToggle from "../components/ThemeToggle"
import { Eye, EyeOff, Shield, Bell, LayoutGrid, Database, KeyRound, LogOut, Cpu, Briefcase } from "lucide-react"

function Settings() {
  const [activeSubTab, setActiveSubTab] = useState("appearance")

  // Notification states
  const [notifyEmail, setNotifyEmail] = useState(true)
  const [notifyWeekly, setNotifyWeekly] = useState(false)
  const [notifyScoring, setNotifyScoring] = useState(true)

  // Password change states
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPass, setShowPass] = useState({ current: false, new: false, confirm: false })
  const [pwdError, setPwdError] = useState("")
  const [pwdSuccess, setPwdSuccess] = useState(false)

  // AI Configurations States
  const [aiModel, setAiModel] = useState(() => localStorage.getItem("aiModel") || "gemini-2.5-flash")
  const [aiStrictness, setAiStrictness] = useState(() => localStorage.getItem("aiStrictness") || "standard")
  const [aiRecruiterMode, setAiRecruiterMode] = useState(() => localStorage.getItem("aiRecruiterMode") || "normal recruiter")
  const [saveAiSuccess, setSaveAiSuccess] = useState(false)

  // Mock settings save state
  const [saveNotifySuccess, setSaveNotifySuccess] = useState(false)

  // Preferred Career Targets States
  const [prefIndustries, setPrefIndustries] = useState(() => localStorage.getItem("preferredIndustries") || "Software Engineering, Artificial Intelligence, Data & Analytics")
  const [prefRoles, setPrefRoles] = useState(() => localStorage.getItem("preferredRoles") || "Frontend Developer, Backend Developer, DevOps Engineer")
  const [prefExpLevel, setPrefExpLevel] = useState(() => localStorage.getItem("preferredExperienceLevel") || "Intermediate")
  const [prefLocation, setPrefLocation] = useState(() => localStorage.getItem("preferredLocation") || "Remote, New York, San Francisco")
  const [saveCareerSuccess, setSaveCareerSuccess] = useState(false)

  function handlePasswordReset(e) {
    e.preventDefault()
    setPwdError("")
    setPwdSuccess(false)

    if (!currentPassword || !newPassword || !confirmPassword) {
      setPwdError("All password fields are required.")
      return
    }

    if (newPassword.length < 6) {
      setPwdError("New password must be at least 6 characters.")
      return
    }

    if (newPassword !== confirmPassword) {
      setPwdError("New passwords do not match.")
      return
    }

    // Success simulation
    setPwdSuccess(true)
    setCurrentPassword("")
    setNewPassword("")
    setConfirmPassword("")

    setTimeout(() => {
      setPwdSuccess(false)
    }, 4000)
  }

  function handleSaveNotifications(e) {
    e.preventDefault()
    setSaveNotifySuccess(true)
    setTimeout(() => {
      setSaveNotifySuccess(false)
    }, 3000)
  }

  function handleSaveAIConfig(e) {
    e.preventDefault()
    localStorage.setItem("aiModel", aiModel)
    localStorage.setItem("aiStrictness", aiStrictness)
    localStorage.setItem("aiRecruiterMode", aiRecruiterMode)
    setSaveAiSuccess(true)
    setTimeout(() => {
      setSaveAiSuccess(false)
    }, 3000)
  }

  function handleSaveCareerConfig(e) {
    e.preventDefault()
    localStorage.setItem("preferredIndustries", prefIndustries)
    localStorage.setItem("preferredRoles", prefRoles)
    localStorage.setItem("preferredExperienceLevel", prefExpLevel)
    localStorage.setItem("preferredLocation", prefLocation)
    setSaveCareerSuccess(true)
    setTimeout(() => {
      setSaveCareerSuccess(false)
    }, 3000)
  }

  const subTabs = [
    { id: "appearance", label: "Appearance", icon: <LayoutGrid size={18} /> },
    { id: "ai", label: "AI Engine Config", icon: <Cpu size={18} /> },
    { id: "career", label: "Career Preferences", icon: <Briefcase size={18} /> },
    { id: "security", label: "Security & Passwords", icon: <Shield size={18} /> },
    { id: "notifications", label: "Notification Rules", icon: <Bell size={18} /> },
    { id: "sessions", label: "Session & System Info", icon: <Database size={18} /> }
  ]

  function handleLogout() {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    window.location.href = "/login"
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-8"
    >
      <div>
        <h1 className="text-5xl font-bold">Settings</h1>
        <p className="text-gray-400 mt-2 text-lg">
          Configure interface appearance, authentication preferences, and system rules.
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-8 items-start">
        {/* SUB NAVIGATION PANEL */}
        <div className="w-full lg:w-72 bg-white/5 border border-white/10 p-3 rounded-3xl backdrop-blur-lg flex lg:flex-col gap-1 overflow-x-auto scrollbar-none">
          {subTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSubTab(tab.id)}
              className={`
                flex items-center gap-3 w-full px-4 py-3.5 rounded-2xl font-semibold text-sm transition-all whitespace-nowrap
                ${activeSubTab === tab.id
                  ? "bg-blue-500 text-white shadow-lg shadow-blue-500/10"
                  : "text-gray-400 hover:text-gray-200 hover:bg-white/5"
                }
              `}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* DETAILS CARDS CONTAINER */}
        <div className="flex-1 w-full">
          {activeSubTab === "appearance" && (
            <SettingsCard
              title="Interface Customization"
              description="Customize application layouts and switch between light and dark modes."
            >
              <div className="space-y-6">
                <ThemeToggle />

                <div className="p-4 bg-white/5 rounded-2xl border border-white/10 text-sm text-gray-400">
                  <h4 className="font-semibold text-gray-200 mb-1">Layout Scale</h4>
                  <p>Our SaaS dashboard is dynamically configured to adapt automatically to your browser zoom level and responsive viewport bounds.</p>
                </div>
              </div>
            </SettingsCard>
          )}

          {activeSubTab === "ai" && (
            <SettingsCard
              title="Gemini AI Engine Configuration"
              description="Configure Google Gemini model parameters, recruiter simulation strictness, and review detailing level."
            >
              <form onSubmit={handleSaveAIConfig} className="space-y-5">
                <div>
                  <label className="block text-sm text-gray-400 font-semibold mb-2">Gemini AI Model Selection</label>
                  <select
                    value={aiModel}
                    onChange={(e) => setAiModel(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
                  >
                    <option value="gemini-2.5-flash">Gemini 2.5 Flash (Fast, Recommended)</option>
                    <option value="gemini-2.5-pro">Gemini 2.5 Pro (Deep Analytics, Slower)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 font-semibold mb-2">Hiring Manager Recruiter Tone</label>
                  <select
                    value={aiRecruiterMode}
                    onChange={(e) => setAiRecruiterMode(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
                  >
                    <option value="normal recruiter">Standard Recruiter (Constructive)</option>
                    <option value="strict hiring manager">Corporate Hiring Director (Highly Critical)</option>
                    <option value="constructive tech mentor">Senior Technical Lead (Development Focused)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 font-semibold mb-2">ATS Strictness Level</label>
                  <select
                    value={aiStrictness}
                    onChange={(e) => setAiStrictness(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
                  >
                    <option value="standard">Standard ATS Filters</option>
                    <option value="strict">Strict Keywords Filtering</option>
                    <option value="permissive">Permissive Evaluation</option>
                  </select>
                </div>

                <div className="flex items-center gap-4">
                  <button
                    type="submit"
                    className="px-6 py-3.5 rounded-2xl bg-blue-500 hover:bg-blue-600 transition font-semibold cursor-pointer"
                  >
                    Save Configuration
                  </button>
                  {saveAiSuccess && (
                    <span className="text-green-400 text-sm font-semibold">AI settings updated successfully!</span>
                  )}
                </div>
              </form>
            </SettingsCard>
          )}

          {activeSubTab === "security" && (
            <SettingsCard
              title="Change Account Password"
              description="Keep your credential payloads updated to maintain secure workspace access."
            >
              <form onSubmit={handlePasswordReset} className="space-y-5">
                {pwdError && (
                  <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-2xl text-sm font-semibold">
                    {pwdError}
                  </div>
                )}
                {pwdSuccess && (
                  <div className="p-4 bg-green-500/10 border border-green-500/20 text-green-400 rounded-2xl text-sm font-semibold">
                    Password changed successfully! Keep note of your new credentials.
                  </div>
                )}

                <div className="relative">
                  <label className="block text-sm text-gray-400 font-semibold mb-2 flex items-center gap-1.5">
                    <KeyRound size={14} /> Current Password
                  </label>
                  <input
                    type={showPass.current ? "text" : "password"}
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 focus:border-blue-500 outline-none rounded-2xl px-5 py-3.5 pr-12 transition"
                    placeholder="Enter current password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass({ ...showPass, current: !showPass.current })}
                    className="absolute right-4 top-[42px] text-gray-400 hover:text-gray-200"
                  >
                    {showPass.current ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>

                <div className="relative">
                  <label className="block text-sm text-gray-400 font-semibold mb-2 flex items-center gap-1.5">
                    <KeyRound size={14} /> New Password
                  </label>
                  <input
                    type={showPass.new ? "text" : "password"}
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 focus:border-blue-500 outline-none rounded-2xl px-5 py-3.5 pr-12 transition"
                    placeholder="Enter new password (min. 6 chars)"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass({ ...showPass, new: !showPass.new })}
                    className="absolute right-4 top-[42px] text-gray-400 hover:text-gray-200"
                  >
                    {showPass.new ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>

                <div className="relative">
                  <label className="block text-sm text-gray-400 font-semibold mb-2 flex items-center gap-1.5">
                    <KeyRound size={14} /> Confirm New Password
                  </label>
                  <input
                    type={showPass.confirm ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 focus:border-blue-500 outline-none rounded-2xl px-5 py-3.5 pr-12 transition"
                    placeholder="Re-type new password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPass({ ...showPass, confirm: !showPass.confirm })}
                    className="absolute right-4 top-[42px] text-gray-400 hover:text-gray-200"
                  >
                    {showPass.confirm ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                </div>

                <button
                  type="submit"
                  className="px-6 py-3.5 rounded-2xl bg-blue-500 hover:bg-blue-600 transition font-semibold"
                >
                  Update Password
                </button>
              </form>
            </SettingsCard>
          )}

          {activeSubTab === "notifications" && (
            <SettingsCard
              title="Notification Configuration"
              description="Control when and how you receive alerts and reports."
            >
              <form onSubmit={handleSaveNotifications} className="space-y-6">
                <div className="space-y-4">
                  <label className="flex items-center gap-3 p-4 bg-white/5 rounded-2xl border border-white/10 cursor-pointer hover:bg-white/10 transition">
                    <input
                      type="checkbox"
                      checked={notifyEmail}
                      onChange={(e) => setNotifyEmail(e.target.checked)}
                      className="w-5 h-5 rounded border-white/10 text-blue-500 bg-slate-950 accent-blue-500 focus:ring-0 focus:ring-offset-0"
                    />
                    <div>
                      <p className="font-semibold text-sm">Email Reports</p>
                      <p className="text-xs text-gray-400">Receive summary reports on email inbox after resume upload analysis completed.</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-4 bg-white/5 rounded-2xl border border-white/10 cursor-pointer hover:bg-white/10 transition">
                    <input
                      type="checkbox"
                      checked={notifyWeekly}
                      onChange={(e) => setNotifyWeekly(e.target.checked)}
                      className="w-5 h-5 rounded border-white/10 text-blue-500 bg-slate-950 accent-blue-500 focus:ring-0 focus:ring-offset-0"
                    />
                    <div>
                      <p className="font-semibold text-sm">Weekly Summary</p>
                      <p className="text-xs text-gray-400">Receive a weekly summary newsletter with detailed ATS history performance tracking metrics.</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 p-4 bg-white/5 rounded-2xl border border-white/10 cursor-pointer hover:bg-white/10 transition">
                    <input
                      type="checkbox"
                      checked={notifyScoring}
                      onChange={(e) => setNotifyScoring(e.target.checked)}
                      className="w-5 h-5 rounded border-white/10 text-blue-500 bg-slate-950 accent-blue-500 focus:ring-0 focus:ring-offset-0"
                    />
                    <div>
                      <p className="font-semibold text-sm">ATS Scoring Optimization Tips</p>
                      <p className="text-xs text-gray-400">Alert me when critical missing skills are identified in parsed resumes.</p>
                    </div>
                  </label>
                </div>

                <div className="flex items-center gap-4">
                  <button
                    type="submit"
                    className="px-6 py-3.5 rounded-2xl bg-blue-500 hover:bg-blue-600 transition font-semibold"
                  >
                    Save Changes
                  </button>
                  {saveNotifySuccess && (
                    <span className="text-green-400 text-sm font-semibold">Changes saved successfully!</span>
                  )}
                </div>
              </form>
            </SettingsCard>
          )}

          {activeSubTab === "career" && (
            <SettingsCard
              title="Target Career Preferences"
              description="Customize your industry, job roles, and locations to guide the AI Matching Engine."
            >
              <form onSubmit={handleSaveCareerConfig} className="space-y-5">
                <div>
                  <label className="block text-sm text-gray-400 font-semibold mb-2">Preferred Industries (comma-separated)</label>
                  <input
                    type="text"
                    value={prefIndustries}
                    onChange={(e) => setPrefIndustries(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
                    placeholder="e.g. Software Engineering, AI, FinTech"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 font-semibold mb-2">Preferred Roles (comma-separated)</label>
                  <input
                    type="text"
                    value={prefRoles}
                    onChange={(e) => setPrefRoles(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
                    placeholder="e.g. Frontend Developer, Full Stack Engineer"
                  />
                </div>

                <div>
                  <label className="block text-sm text-gray-400 font-semibold mb-2">Target Experience Level</label>
                  <select
                    value={prefExpLevel}
                    onChange={(e) => setPrefExpLevel(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
                  >
                    <option value="Junior">Junior (0-2 Years)</option>
                    <option value="Intermediate">Intermediate (3-5 Years)</option>
                    <option value="Senior">Senior (5+ Years)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 font-semibold mb-2">Preferred Location / Remote</label>
                  <input
                    type="text"
                    value={prefLocation}
                    onChange={(e) => setPrefLocation(e.target.value)}
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
                    placeholder="e.g. Remote, San Francisco, India"
                  />
                </div>

                <div className="flex items-center gap-4">
                  <button
                    type="submit"
                    className="px-6 py-3.5 rounded-2xl bg-blue-500 hover:bg-blue-600 transition font-semibold cursor-pointer"
                  >
                    Save Preferences
                  </button>
                  {saveCareerSuccess && (
                    <span className="text-green-400 text-sm font-semibold">Career preferences saved!</span>
                  )}
                </div>
              </form>
            </SettingsCard>
          )}

          {activeSubTab === "sessions" && (
            <SettingsCard
              title="System Sessions Details"
              description="View metadata about your active candidate session and database configuration."
            >
              <div className="space-y-6">
                <div className="divide-y divide-white/5 text-sm">
                  <div className="py-3 flex justify-between">
                    <span className="text-gray-400">FastAPI Connection Port</span>
                    <span className="font-semibold">8000</span>
                  </div>
                  <div className="py-3 flex justify-between">
                    <span className="text-gray-400">Session Handshake Protocol</span>
                    <span className="font-semibold text-green-400">JWT OAuth2 Bearer</span>
                  </div>
                  <div className="py-3 flex justify-between">
                    <span className="text-gray-400">Token Presence Check</span>
                    <span className="font-semibold text-blue-400">Verified</span>
                  </div>
                  <div className="py-3 flex justify-between">
                    <span className="text-gray-400">Client Engine Version</span>
                    <span className="font-semibold text-gray-300">SaaS v1.0.0</span>
                  </div>
                </div>

                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl bg-red-500/10 hover:bg-red-500/20 text-red-400 transition font-semibold border border-red-500/20"
                >
                  <LogOut size={16} /> Sign Out of Platform
                </button>
              </div>
            </SettingsCard>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export default Settings
