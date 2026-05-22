import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts"

const data = [
  { name: "Mon", score: 65 },
  { name: "Tue", score: 70 },
  { name: "Wed", score: 75 },
  { name: "Thu", score: 80 },
  { name: "Fri", score: 82 },
  { name: "Sat", score: 84 },
]

function AnalyticsChart() {

  return (

    <div className="bg-white/5 backdrop-blur-lg border border-white/10 p-6 rounded-2xl mt-10">

      <h2 className="text-2xl font-bold mb-6">
        ATS Score Analytics
      </h2>

      <div className="h-80">

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
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

    </div>

  )
}

export default AnalyticsChart