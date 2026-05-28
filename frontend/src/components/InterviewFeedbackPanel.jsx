import React from 'react'
import { CheckCircle2, TrendingUp, RefreshCw, ArrowRight } from 'lucide-react'

export function InterviewFeedbackPanel({ 
  critique, 
  onNext, 
  onComplete, 
  isLast, 
  completing 
}) {
  return (
    <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6">
      <h3 className="text-2xl font-bold text-gray-200">AI Evaluation</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Score Badge */}
        <div className="p-5 bg-white/5 border border-white/10 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 font-bold text-lg">
            {critique.score}%
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-200">Answer Quality</p>
            <p className="text-xs text-gray-400">Semantic alignment with key concepts</p>
          </div>
        </div>

        {/* Confidence Badge */}
        <div className="p-5 bg-white/5 border border-white/10 rounded-2xl flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400 font-bold text-lg">
            {critique.confidence_score || Math.round(critique.score * 0.9)}%
          </div>
          <div>
            <p className="text-sm font-semibold text-gray-200">Articulation Confidence</p>
            <p className="text-xs text-gray-400">Tone structure and precision</p>
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-gray-300 flex items-center gap-1.5">
            <CheckCircle2 size={16} className="text-green-400" /> Evaluation Critique
          </h4>
          <p className="text-sm text-gray-400 mt-1 leading-relaxed bg-slate-900 border border-white/5 p-4 rounded-xl">
            {critique.ai_evaluation}
          </p>
        </div>

        {critique.improvement_suggestions && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 flex items-center gap-1.5">
              <TrendingUp size={16} className="text-blue-400" /> Improvement Suggestions
            </h4>
            <p className="text-sm text-gray-400 mt-1 leading-relaxed bg-slate-900 border border-white/5 p-4 rounded-xl">
              {critique.improvement_suggestions}
            </p>
          </div>
        )}

        {critique.follow_up_question && (
          <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-2xl space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-purple-400">Adaptive Follow-Up Question</h4>
            <p className="text-sm text-gray-200 leading-relaxed font-semibold">
              "{critique.follow_up_question}"
            </p>
          </div>
        )}
      </div>

      <button
        onClick={isLast ? onComplete : onNext}
        disabled={completing}
        className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/40 disabled:cursor-not-allowed font-semibold rounded-2xl text-white transition shadow-lg shadow-blue-500/20 cursor-pointer"
      >
        {completing ? (
          <>
            <RefreshCw className="animate-spin" size={16} /> Syncing Session Report...
          </>
        ) : isLast ? (
          <>
            Finish Mock Interview & Generate Report <ArrowRight size={16} />
          </>
        ) : (
          <>
            Proceed to Next Question <ArrowRight size={16} />
          </>
        )}
      </button>
    </div>
  )
}

export default InterviewFeedbackPanel
