import Card from "./Card"

function DashboardCards() {
  return (
    <div className="grid grid-cols-3 gap-6">

      <Card
        title="ATS Score"
        value="82%"
      />

      <Card
        title="Skills Found"
        value="14"
      />

      <Card
        title="Job Matches"
        value="8"
      />

      <Card
        title="Resume Uploads"
        value="25"
      />

    </div>
  )
}

export default DashboardCards