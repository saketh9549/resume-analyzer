import React from 'react'
import { Send, HelpCircle } from 'lucide-react'

export function InterviewQuestionCard({ 
  question, 
  userAnswer, 
  setUserAnswer, 
  onSubmit, 
  submitting,
  critique
}) {
  return (
    <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6">
      <div className="flex items-start gap-4">
        <div className="p-3 bg-blue-500/10 rounded-2xl border border-blue-500/20 text-blue-400">
          <HelpCircle size={24} />
        </div>
        <div className="space-y-1">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-400">
            {question.question_type || 'technical'} question
          </span>
          <h3 className="text-xl font-bold text-gray-100 leading-relaxed">{question.question}</h3>
        </div>
      </div>

      <div className="space-y-3">
        <label className="block text-sm text-gray-400 font-semibold">Your Answer</label>
        <textarea
          value={userAnswer}
          onChange={(e) => setUserAnswer(e.target.value)}
          disabled={submitting || !!critique}
          rows={5}
          placeholder="Type your detailed answer here... (Highlight metrics, frameworks, and architecture where applicable)"
          className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl p-5 focus:border-blue-500 transition disabled:opacity-60 disabled:cursor-not-allowed text-sm leading-relaxed"
        />
      </div>

      {!critique && (
        <button
          onClick={onSubmit}
          disabled={submitting || !userAnswer.trim()}
          className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/40 disabled:cursor-not-allowed font-semibold rounded-2xl text-white transition shadow-lg shadow-blue-500/20 cursor-pointer"
        >
          {submitting ? (
            <>Evaluating Answer...</>
          ) : (
            <>
              Submit Answer <Send size={16} />
            </>
          )}
        </button>
      )}
    </div>
  )
}

export default InterviewQuestionCard
