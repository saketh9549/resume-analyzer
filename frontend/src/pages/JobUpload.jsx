import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { postRecruiterJob, getRecruiterJobs } from "../services/api"
import { useToast } from "../context/ToastContext"
import { Briefcase, MapPin, Building, Plus, Check, Loader2, Sparkles, FileText } from "lucide-react"

export default function JobUpload() {
  const { showToast } = useToast()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  // Form Fields
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [department, setDepartment] = useState("Engineering")
  const [location, setLocation] = useState("Remote")
  const [skillsStr, setSkillsStr] = useState("")
  const [expRequired, setExpRequired] = useState(0)

  const fetchJobs = async () => {
    try {
      const list = await getRecruiterJobs()
      setJobs(list)
    } catch (err) {
      console.error("Failed to load recruiter jobs:", err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchJobs()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!title.trim() || !description.trim()) {
      showToast("Job Title and Job Description are required.", "error")
      return
    }

    setSubmitting(true)
    const required_skills = skillsStr
      .split(",")
      .map(s => s.trim())
      .filter(s => s.length > 0)

    try {
      const payload = {
        title,
        description,
        department,
        location,
        required_skills,
        experience_years_required: parseInt(expRequired) || 0
      }
      const res = await postRecruiterJob(payload)
      if (res.error) {
        showToast(res.error, "error")
      } else {
        showToast("Job description posted and semantically indexed!", "success")
        // Reset form
        setTitle("")
        setDescription("")
        setSkillsStr("")
        setExpRequired(0)
        // Refresh listing
        fetchJobs()
      }
    } catch (err) {
      showToast("Failed to post job.", "error")
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      {/* Post Form */}
      <div className="lg:col-span-5 bg-slate-900/60 p-6 md:p-8 rounded-3xl border border-white/5 backdrop-blur-xl h-fit space-y-6">
        <div className="flex items-center gap-3 border-b border-white/5 pb-4">
          <div className="p-2 bg-blue-500/10 rounded-xl text-blue-400">
            <Briefcase size={22} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-100">Post New Role</h3>
            <p className="text-xs text-gray-400 mt-0.5">Publish job description for candidate semantic search matching</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-semibold">
          <div>
            <label className="block text-gray-400 mb-1.5 font-bold uppercase tracking-wider">Job Title *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Senior Full-Stack Engineer"
              className="w-full bg-slate-950/60 border border-white/10 px-4 py-3 rounded-xl text-gray-200 outline-none focus:border-blue-500 transition"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-400 mb-1.5 font-bold uppercase tracking-wider">Department</label>
              <select
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                className="w-full bg-slate-950/60 border border-white/10 px-4 py-3 rounded-xl text-gray-300 outline-none focus:border-blue-500 transition"
              >
                <option value="Engineering">Engineering</option>
                <option value="Product">Product</option>
                <option value="Design">Design</option>
                <option value="Marketing">Marketing</option>
                <option value="Sales">Sales</option>
                <option value="Others">Others</option>
              </select>
            </div>
            <div>
              <label className="block text-gray-400 mb-1.5 font-bold uppercase tracking-wider">Location</label>
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Remote / London"
                className="w-full bg-slate-950/60 border border-white/10 px-4 py-3 rounded-xl text-gray-200 outline-none focus:border-blue-500 transition"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-gray-400 mb-1.5 font-bold uppercase tracking-wider">Exp. Required (Years)</label>
              <input
                type="number"
                min="0"
                value={expRequired}
                onChange={(e) => setExpRequired(e.target.value)}
                className="w-full bg-slate-950/60 border border-white/10 px-4 py-3 rounded-xl text-gray-200 outline-none focus:border-blue-500 transition"
              />
            </div>
            <div>
              <label className="block text-gray-400 mb-1.5 font-bold uppercase tracking-wider">Required Skills (CSV)</label>
              <input
                type="text"
                value={skillsStr}
                onChange={(e) => setSkillsStr(e.target.value)}
                placeholder="React, Docker, Python"
                className="w-full bg-slate-950/60 border border-white/10 px-4 py-3 rounded-xl text-gray-200 outline-none focus:border-blue-500 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-gray-400 mb-1.5 font-bold uppercase tracking-wider">Job Description *</label>
            <textarea
              rows={6}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Paste full responsibilities and qualifications details here..."
              className="w-full bg-slate-950/60 border border-white/10 px-4 py-3 rounded-xl text-gray-200 outline-none focus:border-blue-500 transition resize-none leading-relaxed text-xs"
              required
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 text-white font-bold py-3.5 px-6 rounded-xl transition cursor-pointer shadow-lg shadow-blue-500/20 text-sm mt-2"
          >
            {submitting ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Indexing JD Vector...
              </>
            ) : (
              <>
                <Plus size={16} /> Publish & Index Job
              </>
            )}
          </button>
        </form>
      </div>

      {/* Active Jobs List */}
      <div className="lg:col-span-7 bg-slate-900/60 p-6 md:p-8 rounded-3xl border border-white/5 backdrop-blur-xl space-y-6">
        <div className="flex items-center justify-between border-b border-white/5 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-500/10 rounded-xl text-purple-400">
              <Sparkles size={22} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-100">Active Job Postings</h3>
              <p className="text-xs text-gray-400 mt-0.5">Semantically indexed job profiles in our database</p>
            </div>
          </div>
          <span className="bg-purple-500/10 text-purple-400 px-3 py-1 rounded-full text-xs font-semibold">
            {jobs.length} Posted
          </span>
        </div>

        {loading ? (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="animate-spin text-purple-400" size={32} />
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-20 space-y-3">
            <FileText size={40} className="mx-auto text-gray-600 animate-pulse" />
            <p className="text-sm text-gray-400 italic">No job postings created yet.</p>
          </div>
        ) : (
          <div className="space-y-4 max-h-[600px] overflow-y-auto pr-1">
            {jobs.map((job) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-slate-950/40 border border-white/5 hover:border-white/10 p-5 rounded-2xl space-y-3 transition duration-300 group"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-bold text-gray-200 text-sm group-hover:text-purple-400 transition">
                      {job.title}
                    </h4>
                    <div className="flex items-center gap-4 text-[10px] text-gray-500 mt-1 font-bold">
                      <span className="flex items-center gap-1">
                        <Building size={10} /> {job.department}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin size={10} /> {job.location}
                      </span>
                      {job.experience_years_required > 0 && (
                        <span>{job.experience_years_required}+ Yrs Experience</span>
                      )}
                    </div>
                  </div>
                  <span className="text-[9px] bg-green-500/10 text-green-400 border border-green-500/10 px-2.5 py-0.5 rounded-full font-bold flex items-center gap-1">
                    <Check size={9} /> Indexed
                  </span>
                </div>

                <p className="text-[11px] text-gray-400 line-clamp-3 leading-relaxed">
                  {job.description}
                </p>

                {job.required_skills?.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {job.required_skills.map((skill, i) => (
                      <span key={i} className="px-2 py-0.5 rounded bg-white/5 border border-white/5 text-[9px] text-gray-400 font-semibold">
                        {skill}
                      </span>
                    ))}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
