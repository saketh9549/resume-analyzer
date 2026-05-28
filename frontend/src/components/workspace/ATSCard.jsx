import React from "react"
import { CircularProgressbar, buildStyles } from "react-circular-progressbar"
import "react-circular-progressbar/dist/styles.css"
import { ShieldCheck, AlertCircle, FileText, CheckCircle2, ChevronRight } from "lucide-react"
import { 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar 
} from "recharts"

function ATSCard({ atsData }) {
  if (!atsData) return null

  const score = atsData.ats_score || 0
  const categoryScores = atsData.category_scores || {}
  const missingSkills = atsData.missing_skills || []
  const suggestions = atsData.suggestions || []
  const atsBreakdown = atsData.ats_breakdown || []

  // Color picker for scores
  const getScoreColor = (val) => {
    if (val >= 80) return "#10B981" // emerald
    if (val >= 60) return "#F59E0B" // amber
    return "#EF4444" // rose
  }

  const scoreColor = getScoreColor(score)

  // Map breakdown to radar chart format
  const radarData = atsBreakdown.map(item => ({
    subject: item.title,
    value: item.score,
    fullMark: 100
  }))

  return (
    <div className="bg-slate-900/60 p-6 md:p-8 rounded-3xl border border-white/5 backdrop-blur-xl space-y-8">
      {/* Card Title */}
      <div className="flex items-center gap-3 border-b border-white/5 pb-4">
        <div className="p-2 bg-blue-500/10 rounded-xl text-blue-400">
          <ShieldCheck size={22} />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-100">Advanced NLP ATS Diagnostics</h3>
          <p className="text-xs text-gray-400 mt-0.5">Multi-dimensional semantic parser analysis and scoring matrices</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
        {/* Score Meter & Details */}
        <div className="lg:col-span-4 flex flex-col items-center text-center space-y-4">
          <div className="w-36 h-36">
            <CircularProgressbar
              value={score}
              text={`${score}%`}
              styles={buildStyles({
                pathColor: scoreColor,
                textColor: "#F3F4F6",
                trailColor: "rgba(255, 255, 255, 0.05)",
                textSize: "20px"
              })}
            />
          </div>
          <div>
            <span className="text-[10px] font-black uppercase tracking-widest text-gray-500 block">Overall Match Rating</span>
            <p className="text-sm font-black mt-1" style={{ color: scoreColor }}>
              {score >= 85 ? "Excellent Alignment" : score >= 70 ? "Strong Fit" : score >= 50 ? "Ready with Recommendations" : "Requires Rework"}
            </p>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="lg:col-span-8 w-full h-[260px] flex items-center justify-center">
          {radarData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="70%" data={radarData}>
                <PolarGrid stroke="rgba(255, 255, 255, 0.05)" />
                <PolarAngleAxis 
                  dataKey="subject" 
                  tick={{ fill: 'rgba(255, 255, 255, 0.6)', fontSize: 9, fontWeight: 600 }}
                />
                <PolarRadiusAxis 
                  angle={30} 
                  domain={[0, 100]} 
                  tick={{ fill: 'rgba(255, 255, 255, 0.3)', fontSize: 8 }}
                />
                <Radar
                  name="Candidate"
                  dataKey="value"
                  stroke="#3B82F6"
                  fill="#3B82F6"
                  fillOpacity={0.25}
                />
              </RadarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-gray-500 text-xs italic">Loading semantic score radar chart...</div>
          )}
        </div>
      </div>

      {/* 10-Dimensional Detailed Categories */}
      {atsBreakdown.length > 0 && (
        <div className="space-y-4 pt-4 border-t border-white/5">
          <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-widest block">Scoring Breakdown & Matrix Insights</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {atsBreakdown.map((item, idx) => (
              <div key={idx} className="bg-slate-950/40 p-4 rounded-2xl border border-white/5 space-y-2.5">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-xs text-gray-200">{item.title}</span>
                  <span 
                    className="text-[10px] font-black px-2 py-0.5 rounded-full"
                    style={{ 
                      color: getScoreColor(item.score),
                      backgroundColor: `${getScoreColor(item.score)}15`
                    }}
                  >
                    {item.score}%
                  </span>
                </div>
                <p className="text-[10px] text-gray-400 leading-relaxed">{item.description}</p>
                <div className="flex gap-1.5 items-start text-[10px] text-gray-500 border-t border-white/5 pt-2">
                  <ChevronRight size={10} className="text-gray-400 shrink-0 mt-0.5" />
                  <span className="italic">{item.tip}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-white/5">
        {/* Missing Skills */}
        <div className="bg-slate-950/30 p-5 rounded-2xl border border-white/5 space-y-3">
          <div className="flex items-center gap-2 text-rose-400">
            <AlertCircle size={16} />
            <h5 className="font-bold text-xs uppercase tracking-wider">Identified Missing Keywords</h5>
          </div>
          <p className="text-[11px] text-gray-400 leading-relaxed mb-2">
            ATS engines look for these specific industry terms based on job descriptions in this sector.
          </p>
          {missingSkills.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {missingSkills.map((skill, idx) => (
                <span 
                  key={idx} 
                  className="bg-rose-500/10 border border-rose-500/25 text-rose-400 px-2.5 py-0.5 rounded-md text-[10px] font-bold"
                >
                  +{skill}
                </span>
              ))}
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-emerald-400 text-xs py-2">
              <CheckCircle2 size={14} />
              <span>Zero critical missing keywords detected!</span>
            </div>
          )}
        </div>

        {/* Structural Optimization Suggestions */}
        <div className="bg-slate-950/30 p-5 rounded-2xl border border-white/5 space-y-3">
          <div className="flex items-center gap-2 text-yellow-400">
            <FileText size={16} />
            <h5 className="font-bold text-xs uppercase tracking-wider">ATS Layout Guidelines</h5>
          </div>
          {suggestions.length > 0 ? (
            <ul className="space-y-2 text-xs text-gray-400">
              {suggestions.slice(0, 4).map((item, idx) => (
                <li key={idx} className="flex gap-2 items-start leading-relaxed">
                  <span className="text-yellow-400 font-bold shrink-0">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-500 text-xs italic">No format adjustments required.</p>
          )}
        </div>
      </div>
    </div>
  )
}

export default ATSCard
