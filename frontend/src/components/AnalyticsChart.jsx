import { useState, useEffect } from "react"
import { getAnalyticsHistory } from "../services/api"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts"

function AnalyticsChart() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const history = await getAnalyticsHistory()
        setData(history)
      } catch (err) {
        console.error("Error loading analytics history:", err)
      } finally {
        setLoading(false)
      }
    }
    fetchAnalytics()
  }, [])

  return (

    <div className="bg-white/5 backdrop-blur-lg border border-white/10 p-6 rounded-2xl mt-10">


      <h2 className="text-2xl font-bold mb-6">
        ATS Score Analytics
      </h2>

      <div className="h-80">

        {loading ? (
          <div className="flex items-center justify-center h-full text-gray-400">
            Loading score history...
          </div>
        ) : !data || data.length === 0 || (data.length === 1 && data[0].name === "No Data") ? (
          <div className="flex items-center justify-center h-full text-gray-500 bg-slate-800/20 rounded-xl border border-dashed border-white/10">
            No score history available. Upload a resume to see analytics!
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">

            <LineChart data={data}>

              <XAxis dataKey="name" />

              <YAxis />

              <Tooltip />

              <Line
                type="monotone"
                dataKey="score"
                stroke="#3b82f6"
                strokeWidth={3}
                animationDuration={2000}
              />

            </LineChart>

          </ResponsiveContainer>
        )}

      </div>


    </div>

  )
}

export default AnalyticsChart