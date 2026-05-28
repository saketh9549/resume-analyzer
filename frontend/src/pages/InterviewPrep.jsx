import { useState, useEffect } from "react"
import { useToast } from "../context/ToastContext"
import { useResume } from "../context/ResumeContext"
import { motion, AnimatePresence } from "framer-motion"
import { 
  startMockInterview, 
  submitInterviewAnswer, 
  completeMockInterview, 
  getInterviewHistory 
} from "../services/api"
import { 
  Sparkles, 
  RefreshCw, 
  FileText, 
  AlertCircle, 
  HelpCircle, 
  Send, 
  ArrowRight, 
  CheckCircle2, 
  TrendingUp, 
  Award,
  BookOpen,
  ChevronRight,
  Briefcase
} from "lucide-react"
import ResumeSelector from "../components/ResumeSelector"
import AIInterviewSession from "../components/AIInterviewSession"

function InterviewPrep() {
  const { showToast } = useToast()
  const { resumes, activeResume, loading: loadingResumes } = useResume()

  // Interview Session states
  const [session, setSession] = useState(null)
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0)
  const [userAnswer, setUserAnswer] = useState("")
  const [submittingAnswer, setSubmittingAnswer] = useState(false)
  const [currentCritique, setCurrentCritique] = useState(null)
  
  // Start parameters
  const [jobTitle, setJobTitle] = useState("")
  const [difficulty, setDifficulty] = useState("Intermediate")
  const [interviewMode, setInterviewMode] = useState("Technical")
  const [startingSession, setStartingSession] = useState(false)

  // History & Completion states
  const [history, setHistory] = useState([])
  const [completing, setCompleting] = useState(false)
  const [finalReport, setFinalReport] = useState(null)

  useEffect(() => {
    async function loadHistory() {
      try {
        const hist = await getInterviewHistory()
        setHistory(hist || [])
      } catch (err) {
        console.error(err)
      }
    }
    if (localStorage.getItem("token")) {
      loadHistory()
    }
  }, [finalReport])

  const handleStartInterview = async (e) => {
    e.preventDefault()
    if (!activeResume || !jobTitle) {
      showToast("Please select a resume and enter a target role.", "warning")
      return
    }
    setStartingSession(true)
    setFinalReport(null)
    setSession(null)
    setCurrentQuestionIdx(0)
    setUserAnswer("")
    setCurrentCritique(null)
    try {
      const res = await startMockInterview(activeResume.id, jobTitle, difficulty, interviewMode)
      if (res && !res.error) {
        setSession(res)
        showToast("Mock session loaded successfully!", "success")
      } else {
        showToast(res.error || "Failed to initialize interview.", "error")
      }
    } catch (err) {
      console.error(err)
      showToast("An error occurred starting the interview.", "error")
    } finally {
      setStartingSession(false)
    }
  }

  const handleSubmitAnswer = async () => {
    if (!session || !userAnswer.trim() || submittingAnswer) return
    setSubmittingAnswer(true)
    setCurrentCritique(null)
    try {
      const res = await submitInterviewAnswer(session.session_id, currentQuestionIdx, userAnswer)
      if (res && !res.error) {
        setCurrentCritique(res)
        showToast("Answer evaluated!", "success")
      } else {
        showToast(res.error || "Failed to grade answer.", "error")
      }
    } catch (err) {
      console.error(err)
      showToast("An error occurred evaluating the answer.", "error")
    } finally {
      setSubmittingAnswer(false)
    }
  }

  const handleNextQuestion = () => {
    // Append the evaluated question to local session list so we track evaluations
    const updatedQuestions = [...session.questions]
    updatedQuestions[currentQuestionIdx] = {
      ...updatedQuestions[currentQuestionIdx],
      user_answer: userAnswer,
      score: currentCritique.score,
      confidence_score: currentCritique.confidence_score,
      ai_evaluation: currentCritique.ai_evaluation,
      improvement_suggestions: currentCritique.improvement_suggestions,
      follow_up_question: currentCritique.follow_up_question
    }
    setSession({
      ...session,
      questions: updatedQuestions
    })
    
    setUserAnswer("")
    setCurrentCritique(null)
    setCurrentQuestionIdx(prev => prev + 1)
  }

  const handleCompleteInterview = async () => {
    if (!session || completing) return
    setCompleting(true)
    try {
      const res = await completeMockInterview(session.session_id)
      if (res && !res.error) {
        setFinalReport(res)
        setSession(null)
        showToast("Interview session evaluation compiled!", "success")
      } else {
        showToast(res.error || "Failed to complete interview.", "error")
      }
    } catch (err) {
      console.error(err)
      showToast("An error occurred compiling the report.", "error")
    } finally {
      setCompleting(false)
    }
  }

  const handleRestart = () => {
    setSession(null)
    setFinalReport(null)
    setUserAnswer("")
    setCurrentCritique(null)
    setCurrentQuestionIdx(0)
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AI Interview Prep
          </h1>
          <p className="text-gray-400 mt-2 text-lg">
            Train against custom technical, behavioral, and HR questions with instant AI feedback.
          </p>
        </div>

        {/* Global Resume Selector integration */}
        {!session && !finalReport && (
          <div className="flex flex-col gap-1">
            <span className="text-xs font-semibold text-gray-400">Select Active Workspace Resume:</span>
            <ResumeSelector />
          </div>
        )}
      </div>

      {loadingResumes ? (
        <div className="flex justify-center items-center py-24">
          <RefreshCw className="animate-spin text-blue-400" size={32} />
        </div>
      ) : resumes.length === 0 ? (
        <div className="bg-white/5 border border-white/10 p-12 rounded-3xl text-center space-y-6 max-w-xl mx-auto backdrop-blur-md">
          <AlertCircle size={48} className="mx-auto text-blue-400" />
          <h2 className="text-2xl font-bold text-gray-200">No Resumes Found</h2>
          <p className="text-gray-400 text-sm">
            Please upload a resume first to generate custom mock interview questions.
          </p>
          <a
            href="/upload"
            className="inline-flex items-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 font-semibold rounded-2xl text-white transition-all shadow-lg shadow-blue-500/20"
          >
            Go to Upload <ArrowRight size={16} />
          </a>
        </div>
      ) : (
        <div>
          {/* 1. START SESSION SCREEN */}
          {!session && !finalReport && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Form Config Card */}
              <div className="lg:col-span-2 bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6">
                <div className="border-b border-white/5 pb-4">
                  <h3 className="text-2xl font-bold text-gray-200">Practice Setup</h3>
                  <p className="text-xs text-gray-400 mt-1">Generate questions calibrated to the selected workspace resume details.</p>
                </div>
                
                <form onSubmit={handleStartInterview} className="space-y-5">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-sm text-gray-400 font-semibold mb-2">Target Job Title</label>
                      <input
                        type="text"
                        value={jobTitle}
                        onChange={(e) => setJobTitle(e.target.value)}
                        required
                        placeholder="e.g. Full-Stack Developer"
                        className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition text-sm"
                      />
                    </div>

                    <div>
                      <label className="block text-sm text-gray-400 font-semibold mb-2">Difficulty Grade</label>
                      <select
                        value={difficulty}
                        onChange={(e) => setDifficulty(e.target.value)}
                        className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition text-sm font-semibold cursor-pointer"
                      >
                        <option value="Junior">Junior (0-2 Years Exp)</option>
                        <option value="Intermediate">Intermediate (3-5 Years Exp)</option>
                        <option value="Senior">Senior (5+ Years Exp)</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm text-gray-400 font-semibold mb-3">Interview Mode</label>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                      {["Technical", "Behavioral", "HR", "System Design", "Project Deep Dive"].map(m => (
                        <button
                          key={m}
                          type="button"
                          onClick={() => setInterviewMode(m)}
                          className={`px-3 py-3 rounded-xl border text-xs font-bold transition-all cursor-pointer ${
                            interviewMode === m
                              ? "bg-blue-500/20 text-blue-300 border-blue-500/40"
                              : "bg-white/5 text-gray-400 border-white/5 hover:border-white/10"
                          }`}
                        >
                          {m}
                        </button>
                      ))}
                    </div>
                  </div>

                  {activeResume && (
                    <div className="p-4 bg-blue-500/5 rounded-2xl border border-blue-500/10 flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <FileText size={16} className="text-blue-400" />
                        <span className="text-gray-300 font-semibold truncate max-w-[200px]">{activeResume.name}</span>
                        <span className="px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300 font-bold">{activeResume.score} ATS</span>
                      </div>
                      <span className="text-gray-400">{activeResume.category || "Others"}</span>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={startingSession || !activeResume}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:cursor-not-allowed font-semibold rounded-2xl text-white transition shadow-lg shadow-blue-500/20 cursor-pointer"
                  >
                    {startingSession ? (
                      <>
                        <RefreshCw className="animate-spin" size={16} /> Calibrating System Prompts...
                      </>
                    ) : (
                      <>
                        <Sparkles size={16} /> Start AI Mock Interview
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* History logs card */}
              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md flex flex-col">
                <div className="border-b border-white/5 pb-4 mb-4">
                  <h3 className="text-2xl font-bold text-gray-200 flex items-center gap-2">
                    <TrendingUp size={22} className="text-blue-400" /> Prep History
                  </h3>
                </div>
                
                {history.length === 0 ? (
                  <div className="text-center text-gray-500 text-sm py-12 flex-1 flex items-center justify-center">
                    No past sessions found. Start practicing!
                  </div>
                ) : (
                  <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2 flex-1 scrollbar-thin">
                    {history.map(item => (
                      <div key={item.id} className="p-4 bg-white/5 border border-white/5 rounded-2xl flex justify-between items-center hover:border-white/10 transition">
                        <div>
                          <h5 className="font-bold text-sm text-gray-200">{item.job_title}</h5>
                          <div className="flex items-center gap-1.5 mt-1">
                            <span className="text-[9px] px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-300 font-bold uppercase">{item.mode || "Technical"}</span>
                            <span className="text-[10px] text-gray-400">{item.created_at} • {item.difficulty}</span>
                          </div>
                        </div>
                        {item.readiness_score !== null ? (
                          <span className="px-3 py-1 bg-green-500/10 text-green-400 border border-green-500/10 rounded-xl text-xs font-black">
                            {item.readiness_score}%
                          </span>
                        ) : (
                          <span className="px-3 py-1 bg-yellow-500/10 text-yellow-400 border border-yellow-500/10 rounded-xl text-xs font-bold">
                            Incomplete
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 2. ACTIVE INTERVIEW SESSION */}
          {session && (
            <AIInterviewSession
              session={session}
              activeResume={activeResume}
              currentQuestionIdx={currentQuestionIdx}
              userAnswer={userAnswer}
              setUserAnswer={setUserAnswer}
              onSubmitAnswer={handleSubmitAnswer}
              submittingAnswer={submittingAnswer}
              currentCritique={currentCritique}
              onNextQuestion={handleNextQuestion}
              onCompleteInterview={handleCompleteInterview}
              completing={completing}
            />
          )}

          {/* 3. FINAL COMPLETED REPORT */}
          {finalReport && (
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              className="max-w-2xl mx-auto bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-8"
            >
              <div className="text-center space-y-3">
                <CheckCircle2 size={54} className="mx-auto text-green-400" />
                <h2 className="text-3xl font-black text-gray-200">Mock Interview Complete</h2>
                <p className="text-gray-400 text-sm">
                  Review your score evaluations and constructive feedback.
                </p>
              </div>

              {/* Large gauge display */}
              <div className="flex justify-center items-center py-6">
                <div className="relative w-40 h-40 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="6" fill="transparent" className="text-white/5" />
                    <circle cx="80" cy="80" r="70" stroke="currentColor" strokeWidth="7" fill="transparent" strokeDasharray="439.8" strokeDashoffset={439.8 - (439.8 * finalReport.readiness_score) / 100} className="text-green-400" />
                  </svg>
                  <div className="absolute text-center space-y-0.5">
                    <span className="block text-4xl font-black text-gray-100">{finalReport.readiness_score}%</span>
                    <span className="block text-[10px] text-gray-400 font-bold uppercase tracking-wider">Readiness</span>
                  </div>
                </div>
              </div>

              {/* Feedback paragraph */}
              <div className="p-6 bg-white/5 border border-white/5 rounded-2xl space-y-2">
                <span className="text-xs text-blue-400 font-bold uppercase tracking-wider block">Coach General Evaluation Summary</span>
                <p className="text-sm text-gray-300 leading-relaxed">
                  {finalReport.overall_feedback}
                </p>
              </div>

              <button
                onClick={handleRestart}
                className="w-full py-4 bg-blue-500 hover:bg-blue-600 transition font-semibold rounded-2xl text-white text-center cursor-pointer shadow-lg shadow-blue-500/20"
              >
                Practice Another Mock Session
              </button>
            </motion.div>
          )}
        </div>
      )}
    </div>
  )
}

export default InterviewPrep
