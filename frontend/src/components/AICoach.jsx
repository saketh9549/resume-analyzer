import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { CheckCircle2, AlertTriangle, Lightbulb, UserCheck, Star, Award, MapPin } from "lucide-react"

// Typewriter effect component to animate text display
function Typewriter({ text, speed = 8 }) {
  const [displayedText, setDisplayedText] = useState("")

  useEffect(() => {
    setDisplayedText("")
    if (!text) return

    let index = 0
    const interval = setInterval(() => {
      setDisplayedText((prev) => prev + text.charAt(index))
      index++
      if (index >= text.length) {
        clearInterval(interval)
      }
    }, speed)

    return () => clearInterval(interval)
  }, [text, speed])

  return <span>{displayedText}</span>
}

function AICoach({ feedback }) {
  if (!feedback) {
    return (
      <div className="text-center py-10 text-gray-500 text-sm">
        No AI feedback insights available.
      </div>
    )
  }

  // Set default configurations if fields are empty
  const strengths = feedback.strengths || []
  const weaknesses = feedback.weaknesses || []
  const suggestions = feedback.suggestions || []
  const missingTech = feedback.missing_technologies || []
  const careerReadiness = feedback.career_readiness || "Intermediate"
  const recruiterFeedback = feedback.recruiter_feedback || ""
  const projectFeedback = feedback.project_feedback || []
  const experienceFeedback = feedback.experience_feedback || []
  const learningRoadmap = feedback.learning_recommendations || []

  // Derived readiness badge styles
  let readinessColor = "bg-yellow-500/20 text-yellow-400 border-yellow-500/30"
  if (careerReadiness.toLowerCase().includes("senior") || careerReadiness.toLowerCase().includes("advanced")) {
    readinessColor = "bg-green-500/20 text-green-400 border-green-500/30"
  } else if (careerReadiness.toLowerCase().includes("entry") || careerReadiness.toLowerCase().includes("beginner")) {
    readinessColor = "bg-blue-500/20 text-blue-400 border-blue-500/30"
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-8 mt-6"
    >
      {/* HEADER SUMMARY CARD */}
      <div className="bg-gradient-to-r from-blue-900/40 via-purple-900/40 to-slate-900/40 p-6 rounded-3xl border border-white/10 flex flex-col md:flex-row justify-between items-center gap-6">
        <div>
          <h3 className="text-2xl font-bold flex items-center gap-2">
            🤖 AI Resume Coach Insights
          </h3>
          <p className="text-gray-400 text-sm mt-1">
            recruiter-style assessment and technical keyword audit.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-400 font-semibold">Career Readiness:</span>
          <span className={`px-4 py-1.5 rounded-full border text-sm font-bold tracking-wide ${readinessColor}`}>
            {careerReadiness}
          </span>
        </div>
      </div>

      {/* SECTION 1: AI RESUME COACH (STRENGTHS, WEAKNESSES, SUGGESTIONS) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* STRENGTHS CARD */}
        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-lg">
          <h4 className="text-lg font-bold text-green-400 flex items-center gap-2 mb-4">
            <CheckCircle2 size={20} /> Highlighted Strengths
          </h4>
          <ul className="space-y-3">
            {strengths.map((str, idx) => (
              <motion.li
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="flex items-start gap-2.5 text-sm text-gray-300"
              >
                <span className="text-green-500 mt-0.5">✓</span>
                <span>{str}</span>
              </motion.li>
            ))}
            {strengths.length === 0 && (
              <li className="text-gray-500 text-sm">No specific strengths parsed.</li>
            )}
          </ul>
        </div>

        {/* WEAKNESSES CARD */}
        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-lg">
          <h4 className="text-lg font-bold text-red-400 flex items-center gap-2 mb-4">
            <AlertTriangle size={20} /> ATS Red Flags & Weaknesses
          </h4>
          <ul className="space-y-3">
            {weaknesses.map((weak, idx) => (
              <motion.li
                key={idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.1 }}
                className="flex items-start gap-2.5 text-sm text-gray-300"
              >
                <span className="text-red-500 mt-0.5">⚠️</span>
                <span>{weak}</span>
              </motion.li>
            ))}
            {weaknesses.length === 0 && (
              <li className="text-gray-500 text-sm">No major red flags detected.</li>
            )}
          </ul>
        </div>
      </div>

      {/* OPTIMIZATION SUGGESTIONS CARDS */}
      <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-lg">
        <h4 className="text-lg font-bold text-blue-400 flex items-center gap-2 mb-4">
          <Lightbulb size={20} /> Optimization Recommendations
        </h4>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {suggestions.map((sug, idx) => (
            <motion.li
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              className="p-4 bg-slate-900/50 rounded-2xl border border-white/5 text-sm text-gray-300 flex items-start gap-2"
            >
              <span className="text-blue-400 mt-0.5">•</span>
              <span>{sug}</span>
            </motion.li>
          ))}
        </ul>
      </div>

      {/* SECTION 2: AI RECRUITER REVIEW */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* RECRUITER FEEDBACK IN BOX */}
        <div className="col-span-1 md:col-span-2 bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-lg flex flex-col justify-between">
          <div>
            <h4 className="text-lg font-bold text-purple-400 flex items-center gap-2 mb-4">
              <UserCheck size={20} /> Recruiter Impression
            </h4>
            <div className="p-5 bg-slate-950/80 rounded-2xl border border-white/5 text-gray-300 text-sm italic leading-relaxed relative">
              <span className="absolute -top-3 left-4 text-4xl text-purple-500/30">“</span>
              <p className="relative z-10 pl-2">
                {recruiterFeedback ? <Typewriter text={recruiterFeedback} /> : "Analyzing impression..."}
              </p>
            </div>
          </div>
        </div>

        {/* PROJECT GRADES CARD */}
        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-lg">
          <h4 className="text-lg font-bold text-yellow-400 flex items-center gap-2 mb-4">
            <Star size={20} /> Project Reviews
          </h4>
          <div className="space-y-4 max-h-56 overflow-y-auto pr-1">
            {projectFeedback.map((proj, idx) => (
              <div key={idx} className="p-3 bg-slate-900/60 rounded-xl border border-white/5 space-y-1">
                <div className="flex justify-between items-center">
                  <h5 className="font-bold text-xs text-gray-200 truncate max-w-[120px]">{proj.title}</h5>
                  <span className="text-[10px] bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full font-bold">
                    {proj.rating}
                  </span>
                </div>
                <p className="text-[11px] text-gray-400 line-clamp-2">{proj.feedback}</p>
              </div>
            ))}
            {projectFeedback.length === 0 && (
              <p className="text-gray-500 text-xs py-4 text-center">No projects listed for review.</p>
            )}
          </div>
        </div>
      </div>

      {/* SECTION 3: AI SKILL ADVISOR & ROADMAP */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* MISSING TECH & CERTIFICATIONS */}
        <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-lg flex flex-col justify-between">
          <div>
            <h4 className="text-lg font-bold text-blue-400 flex items-center gap-2 mb-4">
              <Award size={20} /> Recommended Technologies
            </h4>
            <div className="flex flex-wrap gap-2 mb-6">
              {missingTech.map((tech, idx) => (
                <span
                  key={idx}
                  className="text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-semibold"
                >
                  {tech}
                </span>
              ))}
              {missingTech.length === 0 && (
                <span className="text-gray-500 text-sm">Skills checklist matches target standards.</span>
              )}
            </div>
          </div>

          <div className="border-t border-white/5 pt-4">
            <h5 className="text-sm font-bold text-gray-200 mb-2">Target Certifications</h5>
            <div className="space-y-1.5">
              {feedback.certifications?.slice(0, 2).map((cert, idx) => (
                <div key={idx} className="text-xs text-gray-400 flex items-center gap-1.5">
                  <span className="text-blue-500">•</span>
                  <span>{cert}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ROADMAP TIMELINE */}
        <div className="col-span-2 bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-lg">
          <h4 className="text-lg font-bold text-purple-400 flex items-center gap-2 mb-4">
            <MapPin size={20} /> Learning Roadmap Timeline
          </h4>
          <div className="space-y-4">
            {learningRoadmap.map((step, idx) => (
              <div key={idx} className="flex gap-4 items-start">
                <div className="w-6 h-6 rounded-full bg-purple-500/20 border border-purple-500/40 text-purple-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
                  {idx + 1}
                </div>
                <div className="p-3 bg-slate-900/50 rounded-2xl border border-white/5 text-sm text-gray-300 w-full">
                  {step}
                </div>
              </div>
            ))}
            {learningRoadmap.length === 0 && (
              <p className="text-gray-500 text-sm text-center py-6">No learning path suggested.</p>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export default AICoach
