import { useState, useEffect } from "react"
import { getLiveJobs, getRecentUploads } from "../services/api"
import { Briefcase, MapPin, DollarSign, ExternalLink, RefreshCw, AlertCircle, Search } from "lucide-react"

function LiveJobs() {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [skillsFilter, setSkillsFilter] = useState("")
  const [resumes, setResumes] = useState([])

  useEffect(() => {
    async function loadData() {
      try {
        const uploads = await getRecentUploads()
        setResumes(uploads)

        // Load initial live jobs
        const jobData = await getLiveJobs()
        setJobs(jobData)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const handleSearchSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const data = await getLiveJobs(skillsFilter)
      setJobs(data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Title */}
      <div>
        <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          Live Remote Jobs
        </h1>
        <p className="text-gray-400 mt-2 text-lg">
          Explore live remote positions fetched dynamically from global indices, matching your skill criteria.
        </p>
      </div>

      {/* Search Filter Bar */}
      <div className="bg-white/5 border border-white/10 p-5 rounded-3xl backdrop-blur-md">
        <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-4 items-center">
          <div className="flex-1 w-full flex items-center gap-3 bg-slate-900 border border-white/10 px-5 py-3.5 rounded-2xl focus-within:border-blue-500 transition">
            <Search size={18} className="text-gray-400" />
            <input
              type="text"
              value={skillsFilter}
              onChange={(e) => setSkillsFilter(e.target.value)}
              placeholder="Filter jobs by specific skills (comma separated, e.g. React, Python, AWS)..."
              className="flex-1 bg-transparent text-gray-200 outline-none text-sm placeholder-gray-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full sm:w-auto px-6 py-3.5 bg-blue-500 hover:bg-blue-600 transition font-semibold rounded-2xl text-white cursor-pointer shadow-lg shadow-blue-500/20 shrink-0"
          >
            Filter Jobs
          </button>
        </form>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-24">
          <RefreshCw className="animate-spin text-blue-400" size={32} />
        </div>
      ) : jobs.length === 0 ? (
        <div className="bg-white/5 border border-white/10 p-16 rounded-3xl text-center space-y-4 max-w-xl mx-auto backdrop-blur-md">
          <AlertCircle size={40} className="mx-auto text-blue-400" />
          <h3 className="text-xl font-bold text-gray-200">No Matching Jobs</h3>
          <p className="text-gray-400 text-sm">
            Could not find any active postings matching your search filters. Try removing specific skill restrictions.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <div
              key={job.id}
              className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md flex flex-col justify-between hover:border-blue-500/30 transition duration-300 group"
            >
              <div className="space-y-4">
                <div className="flex justify-between items-start gap-3">
                  <div>
                    <h4 className="font-bold text-gray-200 text-base group-hover:text-blue-400 transition leading-snug">
                      {job.title}
                    </h4>
                    <span className="text-xs text-gray-400 block mt-1">{job.company_name}</span>
                  </div>
                  {job.matching_skills_count !== undefined && (
                    <span className="shrink-0 px-2 py-0.5 rounded bg-green-500/10 text-green-400 border border-green-500/10 text-[10px] font-bold">
                      {job.matching_skills_count} Matches
                    </span>
                  )}
                </div>

                <p className="text-xs text-gray-400 leading-relaxed font-medium">
                  {job.description}
                </p>

                {/* Job Meta Metadata */}
                <div className="flex flex-wrap gap-2 pt-2 text-[10px]">
                  <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 border border-white/5 text-gray-400 font-semibold">
                    <MapPin size={10} className="text-blue-400" /> {job.candidate_required_location}
                  </span>
                  <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-white/5 border border-white/5 text-gray-400 font-semibold">
                    <DollarSign size={10} className="text-green-400" /> {job.salary}
                  </span>
                </div>
              </div>

              <div className="pt-6">
                <a
                  href={job.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-xl bg-blue-500/10 hover:bg-blue-500 text-blue-400 hover:text-white border border-blue-500/20 group-hover:border-blue-500/50 transition-all font-bold text-xs"
                >
                  Apply & View Position <ExternalLink size={12} />
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default LiveJobs
