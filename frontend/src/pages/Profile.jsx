import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { getDashboardStats, getRecentUploads } from "../services/api"
import ProfileCard from "../components/ProfileCard"
import { User, Mail, Calendar, FileText, TrendingUp, Briefcase } from "lucide-react"

function Profile() {
  const [user, setUser] = useState(() => {
    try {
      const raw = localStorage.getItem("user")
      return raw ? JSON.parse(raw) : { name: "User", email: "user@example.com" }
    } catch {
      return { name: "User", email: "user@example.com" }
    }
  })

  const [stats, setStats] = useState({
    avg_score: "0%",
    skills_found: "0",
    job_matches: "0",
    total_uploads: "0"
  })

  const [uploads, setUploads] = useState([])
  const [isEditing, setIsEditing] = useState(false)
  const [editName, setEditName] = useState(user.name)
  const [saveSuccess, setSaveSuccess] = useState(false)

  useEffect(() => {
    async function loadData() {
      const dashboardStats = await getDashboardStats()
      const recentUploads = await getRecentUploads()
      if (dashboardStats) setStats(dashboardStats)
      if (recentUploads) setUploads(recentUploads)
    }
    loadData()
  }, [])

  function handleSave(e) {
    e.preventDefault()
    if (!editName.trim()) return

    const updatedUser = { ...user, name: editName.trim() }
    localStorage.setItem("user", JSON.stringify(updatedUser))
    setUser(updatedUser)
    setIsEditing(false)
    setSaveSuccess(true)

    // Trigger window event so that other components (like Navbar) know to update the user name greeting
    window.dispatchEvent(new Event("storage"))

    setTimeout(() => {
      setSaveSuccess(false)
    }, 3000)
  }

  // Get user initial for avatar placeholder
  const initial = user.name ? user.name.charAt(0).toUpperCase() : "U"

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-8"
    >
      <div>
        <h1 className="text-5xl font-bold">My Profile</h1>
        <p className="text-gray-400 mt-2 text-lg">
          Manage your account profile details and overview resume logs.
        </p>
      </div>

      {/* PROFILE HEADER CARD */}
      <ProfileCard className="p-8">
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="w-24 h-24 rounded-full bg-blue-600 flex items-center justify-center text-4xl font-bold shadow-lg shadow-blue-500/20">
            {initial}
          </div>

          <div className="flex-1 text-center md:text-left space-y-2">
            <h2 className="text-3xl font-bold">{user.name}</h2>
            <p className="text-gray-400 text-lg flex items-center justify-center md:justify-start gap-2">
              <Mail size={18} /> {user.email}
            </p>
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-4 text-sm text-gray-500 mt-2">
              <span className="bg-white/5 border border-white/10 px-3 py-1 rounded-full flex items-center gap-1.5">
                <Calendar size={14} /> Active Session
              </span>
              <span className="bg-green-500/10 border border-green-500/20 text-green-400 px-3 py-1 rounded-full">
                SaaS Candidate
              </span>
            </div>
          </div>

          <button
            onClick={() => {
              setEditName(user.name)
              setIsEditing(!isEditing)
            }}
            className="px-6 py-3 rounded-2xl bg-white/5 border border-white/10 hover:bg-white/10 transition font-semibold"
          >
            {isEditing ? "Cancel" : "Edit Profile"}
          </button>
        </div>

        {/* EDIT PROFILE FORM */}
        {isEditing && (
          <motion.form
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            onSubmit={handleSave}
            className="mt-6 pt-6 border-t border-white/5 space-y-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 font-semibold mb-2">Display Name</label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full bg-white/5 border border-white/10 focus:border-blue-500 outline-none rounded-2xl px-5 py-3.5 transition"
                  placeholder="Enter your name"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 font-semibold mb-2">Email Address (Read-only)</label>
                <input
                  type="email"
                  value={user.email}
                  disabled
                  className="w-full bg-white/5 border border-white/5 text-gray-500 outline-none rounded-2xl px-5 py-3.5 cursor-not-allowed"
                />
              </div>
            </div>
            <div className="flex gap-2 justify-end">
              <button
                type="submit"
                className="px-6 py-3 rounded-2xl bg-blue-500 hover:bg-blue-600 transition font-semibold"
              >
                Save Changes
              </button>
            </div>
          </motion.form>
        )}

        {saveSuccess && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-green-500/10 border border-green-500/20 text-green-400 rounded-2xl text-center text-sm font-semibold"
          >
            Profile details updated successfully!
          </motion.div>
        )}
      </ProfileCard>

      {/* STATS HIGHLIGHTS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <ProfileCard>
          <div className="flex items-center gap-4">
            <div className="p-4 bg-blue-500/10 text-blue-400 rounded-2xl border border-blue-500/20">
              <FileText size={28} />
            </div>
            <div>
              <p className="text-sm text-gray-400 font-semibold">Total Resumes Uploaded</p>
              <p className="text-4xl font-extrabold text-white mt-1">{stats.total_uploads}</p>
            </div>
          </div>
        </ProfileCard>

        <ProfileCard>
          <div className="flex items-center gap-4">
            <div className="p-4 bg-green-500/10 text-green-400 rounded-2xl border border-green-500/20">
              <TrendingUp size={28} />
            </div>
            <div>
              <p className="text-sm text-gray-400 font-semibold">Average ATS Score</p>
              <p className="text-4xl font-extrabold text-white mt-1">{stats.avg_score}</p>
            </div>
          </div>
        </ProfileCard>

        <ProfileCard>
          <div className="flex items-center gap-4">
            <div className="p-4 bg-purple-500/10 text-purple-400 rounded-2xl border border-purple-500/20">
              <Briefcase size={28} />
            </div>
            <div>
              <p className="text-sm text-gray-400 font-semibold">Job Market Matches</p>
              <p className="text-4xl font-extrabold text-white mt-1">{stats.job_matches}</p>
            </div>
          </div>
        </ProfileCard>
      </div>

      {/* RECENT UPLOADS SUMMARY */}
      <ProfileCard title="Recent Resume History">
        {uploads.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="border-b border-white/5 text-gray-400 text-sm font-semibold">
                  <th className="py-4">File Name</th>
                  <th className="py-4">ATS Match</th>
                  <th className="py-4">Upload Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 text-sm">
                {uploads.slice(0, 5).map((item) => (
                  <tr key={item.id} className="hover:bg-white/5 transition-colors duration-150">
                    <td className="py-4 font-medium text-gray-100 flex items-center gap-2.5">
                      <span className="text-lg">📄</span> {item.name}
                    </td>
                    <td className="py-4">
                      <span className="px-2.5 py-1 rounded bg-blue-500/20 text-blue-400 font-bold">
                        {item.score}
                      </span>
                    </td>
                    <td className="py-4 text-gray-400">{item.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-10 text-gray-500 text-sm">
            No uploaded resumes found. Go to the Upload tab to start scanning!
          </div>
        )}
      </ProfileCard>
    </motion.div>
  )
}

export default Profile
