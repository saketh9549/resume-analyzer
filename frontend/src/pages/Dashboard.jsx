import DashboardCards from "../components/DashboardCards"
import AnalyticsChart from "../components/AnalyticsChart"
import RecentUploads from "../components/RecentUploads"



function Dashboard() {
  return (
    <div className="animate-fadeIn">
        

      <DashboardCards />
      <AnalyticsChart />
      <RecentUploads />

    </div>
  )
}

export default Dashboard