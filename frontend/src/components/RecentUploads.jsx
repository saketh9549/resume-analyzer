import { useState, useEffect } from "react"
import { getRecentUploads } from "../services/api"
import { Link } from "react-router-dom"

function RecentUploads() {
  const [uploads, setUploads] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchUploads() {
      try {
        const data = await getRecentUploads()
        setUploads(data)
      } catch (err) {
        console.error("Error fetching recent uploads:", err)
      } finally {
        setLoading(false)
      }
    }
    fetchUploads()
  }, [])

  return (

    <div className="bg-slate-900 p-6 rounded-2xl mt-10 border border-white/5">

      <div className="flex items-center justify-between mb-6">

        <h2 className="text-2xl font-bold">
          Recent Uploads
        </h2>

        <Link
          to="/upload"
          className="
            bg-blue-500
            px-4
            py-2
            rounded-xl
            hover:bg-blue-600
            transition
            text-sm
            font-medium
          "
        >
          Upload New
        </Link>

      </div>

      {/* Table Header */}
      <div
        className="
          grid
          grid-cols-3
          text-gray-400
          border-b
          border-slate-700
          pb-3
        "
      >

        <p>Resume Name</p>
        <p>ATS Score</p>
        <p>Upload Date</p>

      </div>

      {/* Table Rows */}
      <div className="mt-4 space-y-4">

        {loading ? (
          <div className="text-center py-6 text-gray-500">
            Loading recent uploads...
          </div>
        ) : uploads.length === 0 ? (
          <div className="text-center py-8 text-gray-400 bg-slate-800/40 rounded-xl">
            <p className="mb-3">No resumes uploaded yet.</p>
            <Link to="/upload" className="text-blue-400 hover:text-blue-300 underline text-sm">
              Upload your first resume now
            </Link>
          </div>
        ) : (
          uploads.map((upload, index) => (

            <div
              key={upload.id || index}
              className="
                grid
                grid-cols-3
                bg-slate-800
                p-4
                rounded-xl
                hover:bg-slate-700/80
                transition
                border
                border-white/5
              "
            >

              <p className="font-medium truncate pr-4">{upload.name}</p>

              <p className="text-green-400 font-semibold">
                {upload.score}
              </p>

              <p className="text-gray-400">{upload.date}</p>

            </div>

          ))
        )}

      </div>

    </div>

  )
}


export default RecentUploads