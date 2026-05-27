import React from "react"
import { CircularProgressbar, buildStyles } from "react-circular-progressbar"
import "react-circular-progressbar/dist/styles.css"
import { ShieldCheck, AlertCircle, FileText, CheckCircle2 } from "lucide-react"

function ATSCard({ atsData }) {
  if (!atsData) return null

  const score = atsData.ats_score || 0
  const categoryScores = atsData.category_scores || {}
  const missingSkills = atsData.missing_skills || []
  const suggestions = atsData.suggestions || []

  // Color picker for scores
  const getScoreColor = (val) => {
    if (val >= 80) return "#10B981" // emerald
    if (val >= 60) return "#F59E0B" // amber
    return "#EF4444" // rose
  }

  const scoreColor = getScoreColor(score)

  return (
    <div className="bg-slate-900/60 p-6 md:p-8 rounded-3xl border border-white/5 backdrop-blur-xl space-y-8">
      {/* Card Title */}
      <div className="flex items-center gap-3 border-b border-white/5 pb-4">
        <div className="p-2 bg-blue-500/10 rounded-xl text-blue-400">
          <ShieldCheck size={22} />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-100">ATS Engine Diagnostics</h3>
          <p className="text-xs text-gray-400 mt-0.5">Automated Application Tracking System validation matches</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
        {/* Score Meter */}
        <div className="md:col-span-4 flex flex-col items-center text-center space-y-4">
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
            <span className="text-xs font-black uppercase tracking-wider text-gray-500">Overall Match Rating</span>
            <p className="text-sm font-bold mt-1" style={{ color: scoreColor }}>
              {score >= 80 ? "Highly Optimised" : score >= 60 ? "Ready with Recommendations" : "Needs Structural Rework"}
            </p>
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="md:col-span-8 space-y-4">
          <h4 className="text-xs font-bold text-blue-400 uppercase tracking-widest block mb-1">Section Scoring Breakdown</h4>
          {Object.entries(categoryScores).length > 0 ? (
            <div className="space-y-3.5">
              {Object.entries(categoryScores).map(([category, val]) => (
                <div key={category} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-gray-300 capitalize">{category.replace(/_/g, ' ')}</span>
                    <span className="font-extrabold" style={{ color: getScoreColor(val) }}>{val}%</span>
                  </div>
                  <div className="w-full bg-white/5 rounded-full h-2">
                    <div
                      className="h-2 rounded-full transition-all duration-700"
                      style={{ 
                        width: `${val}%`,
                        backgroundColor: getScoreColor(val)
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-xs italic">No section score categories detected.</p>
          )}
        </div>
      </div>

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
