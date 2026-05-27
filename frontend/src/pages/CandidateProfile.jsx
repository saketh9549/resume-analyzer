import React, { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { getAnalysisResults, getPreviewUrl } from "../services/resumeApi"
import { 
  ArrowLeft, 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  FileText, 
  Award, 
  Sparkles, 
  LayoutGrid, 
  Briefcase, 
  GraduationCap 
} from "lucide-react"

import ATSCard from "../components/workspace/ATSCard"
import AICoach from "../components/AICoach"

export default function CandidateProfile({ candidateId, onBack }) {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")

  useEffect(() => {
    async function fetchDetails() {
      if (!candidateId) return
      setLoading(true)
      try {
        const data = await getAnalysisResults(candidateId)
        setResults(data)
      } catch (err) {
        setError("Failed to fetch candidate analysis details.")
      } finally {
        setLoading(false)
      }
    }
    fetchDetails()
  }, [candidateId])

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-32 space-y-4">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-gray-400 font-semibold">Loading Candidate Dossier...</p>
      </div>
    )
  }

  if (error || !results) {
    return (
      <div className="bg-rose-500/10 border border-rose-500/20 p-8 rounded-3xl text-center space-y-4 max-w-lg mx-auto">
        <p className="text-rose-400 font-bold">{error || "Failed to load candidate."}</p>
        <button onClick={onBack} className="px-5 py-2.5 bg-white/5 hover:bg-white/10 text-xs font-bold rounded-xl transition text-gray-300">
          Back to Directory
        </button>
      </div>
    )
  }

  const { parsed_data, ai_feedback, multimodal_analysis, ats_score } = results
  const previewUrl = getPreviewUrl(candidateId)

  return (
    <div className="space-y-6">
      {/* Back link */}
      <button 
        onClick={onBack}
        className="flex items-center gap-2 text-xs font-bold text-gray-400 hover:text-blue-400 transition cursor-pointer"
      >
        <ArrowLeft size={14} /> Back to Candidate Directory
      </button>

      {/* Header Panel */}
      <div className="bg-slate-900/60 p-6 md:p-8 rounded-3xl border border-white/5 backdrop-blur-xl flex flex-col md:flex-row justify-between gap-6">
        <div className="flex gap-4">
          <div className="w-16 h-16 bg-blue-500/10 border border-blue-500/25 text-blue-400 rounded-2xl flex items-center justify-center shrink-0 shadow-lg">
            <User size={32} />
          </div>
          <div className="space-y-1">
            <h2 className="text-2xl font-black text-gray-100 leading-none">{results.filename}</h2>
            <div className="flex flex-wrap gap-4 text-xs text-gray-400 pt-1.5 font-bold">
              {parsed_data?.contact?.email && (
                <span className="flex items-center gap-1.5"><Mail size={12} /> {parsed_data.contact.email}</span>
              )}
              {parsed_data?.contact?.phone && (
                <span className="flex items-center gap-1.5"><Phone size={12} /> {parsed_data.contact.phone}</span>
              )}
              {parsed_data?.contact?.location && (
                <span className="flex items-center gap-1.5"><MapPin size={12} /> {parsed_data.contact.location}</span>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-col md:items-end justify-center shrink-0 border-t md:border-t-0 border-white/5 pt-4 md:pt-0">
          <span className="text-[10px] text-gray-500 uppercase tracking-widest font-black">Overall ATS Rating</span>
          <span className="text-4xl font-extrabold text-blue-400 block mt-1">{ats_score}%</span>
        </div>
      </div>

      {/* Layout split: dossier info vs CV preview */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* dossier details (Experience, Skills, Coach review) */}
        <div className="lg:col-span-7 space-y-8">
          
          {/* ATS Diagnostics */}
          <ATSCard atsData={results} />

          {/* AI rec reviews */}
          {ai_feedback && (
            <div className="space-y-3">
              <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                <Sparkles size={18} className="text-purple-400" /> AI Recruiter Coaching Review
              </h3>
              <AICoach feedback={ai_feedback} />
            </div>
          )}

          {/* Visual audit */}
          {multimodal_analysis ? (
            <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 backdrop-blur-xl space-y-6">
              <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
                <LayoutGrid size={18} className="text-purple-400" /> Gemini Vision Visual Layout Diagnostics
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[
                  { label: "Layout Quality", score: multimodal_analysis.visual_scores?.layout_score },
                  { label: "Design Consistency", score: multimodal_analysis.visual_scores?.design_score },
                  { label: "Readability Spacing", score: multimodal_analysis.visual_scores?.readability_score },
                  { label: "Formatting Alignment", score: multimodal_analysis.visual_scores?.formatting_score },
                ].map((dim, i) => (
                  <div key={i} className="bg-slate-950/60 p-4 rounded-xl border border-white/5 flex flex-col justify-between h-20">
                    <span className="text-[9px] text-gray-500 font-bold leading-tight uppercase block">{dim.label}</span>
                    <span className="text-2xl font-extrabold text-blue-400 block mt-2">{dim.score}%</span>
                  </div>
                ))}
              </div>
              <div className="p-4 bg-slate-950/40 border border-white/5 rounded-2xl text-xs leading-relaxed">
                <span className="font-bold text-purple-400 block mb-1">Layout Feedback</span>
                <p className="text-gray-300">{multimodal_analysis.layout_feedback}</p>
              </div>
            </div>
          ) : (
            <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 text-center py-6 text-gray-500 text-xs italic">
              Visual layout diagnostics is only available for PDF documents.
            </div>
          )}

          {/* Work History */}
          <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 backdrop-blur-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
              <Briefcase size={18} className="text-blue-400" /> Professional Experience
            </h3>
            {parsed_data?.experience?.length > 0 ? (
              <div className="space-y-4">
                {parsed_data.experience.map((exp, idx) => (
                  <div key={idx} className="border-l border-white/10 pl-4 py-1 space-y-1 text-xs">
                    <h4 className="font-bold text-gray-200 text-sm">{exp.role || exp.title || "Experience Position"}</h4>
                    <div className="text-[10px] text-gray-400 font-semibold">{exp.company || "Company"} | {exp.duration || exp.dates || "Duration"}</div>
                    {exp.description && (
                      <p className="text-[11px] text-gray-500 leading-relaxed pt-1">{exp.description}</p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 italic">No structured experience history detected.</p>
            )}
          </div>

          {/* Education */}
          <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 backdrop-blur-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2">
              <GraduationCap size={18} className="text-blue-400" /> Education History
            </h3>
            {parsed_data?.education?.length > 0 ? (
              <div className="space-y-3 text-xs">
                {parsed_data.education.map((edu, idx) => (
                  <div key={idx} className="border-l border-white/10 pl-4 py-1 space-y-1">
                    <h4 className="font-bold text-gray-200 text-sm">{edu.degree || edu.qualification || "Degree"}</h4>
                    <div className="text-[10px] text-gray-400 font-semibold">{edu.institution || edu.school || "School / University"} | {edu.duration || edu.year || "Year"}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-500 italic">No education credentials detected.</p>
            )}
          </div>

        </div>

        {/* CV Preview side pane */}
        <div className="lg:col-span-5 space-y-4 h-fit">
          <div className="bg-slate-900/60 p-6 rounded-3xl border border-white/5 backdrop-blur-xl space-y-4">
            <h3 className="text-lg font-bold text-gray-200 flex items-center gap-2 border-b border-white/5 pb-3">
              <FileText size={18} className="text-blue-400" /> Original CV Document
            </h3>
            <div className="h-[650px] bg-slate-950/40 rounded-2xl border border-white/10 overflow-hidden">
              <iframe src={previewUrl} className="w-full h-full border-none" title="Candidate CV Document" />
            </div>
          </div>
        </div>

      </div>
    </div>
  )
}
