import React from 'react'
import { FileText, Sparkles } from 'lucide-react'
import InterviewQuestionCard from './InterviewQuestionCard'
import InterviewFeedbackPanel from './InterviewFeedbackPanel'

export function AIInterviewSession({
  session,
  activeResume,
  currentQuestionIdx,
  userAnswer,
  setUserAnswer,
  onSubmitAnswer,
  submittingAnswer,
  currentCritique,
  onNextQuestion,
  onCompleteInterview,
  completing
}) {
  const currentQuestion = session.questions[currentQuestionIdx]
  const isLast = currentQuestionIdx === session.questions.length - 1

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      {/* Main Interview Panel (Col 2) */}
      <div className="lg:col-span-2 space-y-6">
        {/* Progress header */}
        <div className="flex items-center justify-between bg-white/5 border border-white/10 p-5 rounded-2xl">
          <div className="flex items-center gap-3">
            <span className="px-3 py-1 rounded bg-blue-500/20 text-blue-300 font-bold text-xs">
              Question {currentQuestionIdx + 1} of {session.questions.length}
            </span>
            <span className="text-gray-400 text-xs font-semibold uppercase tracking-wider">
              Mode: {session.mode || 'Technical'}
            </span>
          </div>
          <div className="flex gap-1.5">
            {session.questions.map((_, i) => (
              <div 
                key={i} 
                className={`w-8 h-1.5 rounded-full transition-all ${
                  i < currentQuestionIdx 
                    ? 'bg-green-500' 
                    : i === currentQuestionIdx 
                      ? 'bg-blue-500 animate-pulse' 
                      : 'bg-white/10'
                }`} 
              />
            ))}
          </div>
        </div>

        {/* Dynamic Card */}
        {currentCritique ? (
          <InterviewFeedbackPanel
            critique={currentCritique}
            onNext={onNextQuestion}
            onComplete={onCompleteInterview}
            isLast={isLast}
            completing={completing}
          />
        ) : (
          <InterviewQuestionCard
            question={currentQuestion}
            userAnswer={userAnswer}
            setUserAnswer={setUserAnswer}
            onSubmit={onSubmitAnswer}
            submitting={submittingAnswer}
            critique={null}
          />
        )}
      </div>

      {/* Side Intelligence Panel (Col 1) */}
      <div className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md space-y-6 self-start">
        <div className="flex items-center gap-2 border-b border-white/5 pb-4">
          <FileText className="text-blue-400" size={18} />
          <h4 className="font-bold text-gray-200 text-sm">Resume Intelligence</h4>
        </div>

        {activeResume && (
          <div className="space-y-4">
            <div>
              <p className="text-xs text-gray-400">Selected Resume</p>
              <p className="text-sm font-semibold text-gray-200 truncate mt-0.5">{activeResume.name}</p>
            </div>

            <div>
              <p className="text-xs text-gray-400">ATS Competency Score</p>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex-1 bg-white/10 h-2 rounded-full overflow-hidden">
                  <div 
                    className="bg-blue-500 h-full transition-all duration-500" 
                    style={{ width: activeResume.score || '0%' }}
                  />
                </div>
                <span className="text-xs font-bold text-blue-400">{activeResume.score}</span>
              </div>
            </div>

            <div>
              <p className="text-xs text-gray-400">Primary Skills Identified</p>
              <div className="flex flex-wrap gap-1.5 mt-2">
                {activeResume.skills?.slice(0, 8).map((s, idx) => (
                  <span key={idx} className="text-[10px] px-2 py-1 rounded bg-white/5 text-gray-300 font-semibold border border-white/5">
                    {s}
                  </span>
                )) || <span className="text-xs text-gray-500">None detected</span>}
              </div>
            </div>

            <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-2xl space-y-1">
              <p className="text-xs font-bold text-yellow-400 uppercase tracking-wide flex items-center gap-1">
                <Sparkles size={12} /> Weakness Focus Areas
              </p>
              <p className="text-[11px] text-gray-400 leading-relaxed">
                The questions are calibrated to verify: {activeResume.ats_weaknesses?.slice(0, 2).join(', ') || 'System Design, Security'}.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default AIInterviewSession
