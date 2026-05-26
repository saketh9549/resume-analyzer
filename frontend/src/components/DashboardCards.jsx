import { useState, useEffect } from "react"
import { getDashboardStats } from "../services/api"
import Card from "./Card"

function DashboardCards() {
  const [stats, setStats] = useState({
    avg_score: "0%",
    skills_found: "0",
    job_matches: "0",
    total_uploads: "0"
  })

  useEffect(() => {
    async function fetchStats() {
      try {
        const data = await getDashboardStats()
        setStats(data)
      } catch (err) {
        console.error("Error loading dashboard stats:", err)
      }
    }
    fetchStats()
  }, [])

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">

      <Card
        title="Average ATS Score"
        value={stats.avg_score}
      />

      <Card
        title="Skills Found"
        value={stats.skills_found}
      />

      <Card
        title="Job Matches"
        value={stats.job_matches}
      />

      <Card
        title="Total Uploads"
        value={stats.total_uploads}
      />

    </div>
  )
}


export default DashboardCards