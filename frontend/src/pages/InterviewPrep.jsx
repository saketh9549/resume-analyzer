import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  getRecentUploads, 
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
  BookOpen
} from "lucide-react"

function InterviewPrep() {
  const [resumes, setResumes] = useState([])
  const [selectedResumeId, setSelectedResumeId] = useState("")
  const [loadingResumes, setLoadingResumes] = useState(true)

  // Interview Session states
  const [session, setSession] = useState(null) // active interview session
  const [currentQuestionIdx, setCurrentQuestionIdx] = useState(0)
  const [userAnswer, setUserAnswer] = useState("")
  const [submittingAnswer, setSubmittingAnswer] = useState(false)
  const [currentCritique, setCurrentCritique] = useState(null)
  
  // Start parameters
  const [jobTitle, setJobTitle] = useState("")
  const [difficulty, setDifficulty] = useState("Intermediate")
  const [startingSession, setStartingSession] = useState(false)

  // History & Completion states
  const [history, setHistory] = useState([])
  const [completing, setCompleting] = useState(false)
  const [finalReport, setFinalReport] = useState(null)

  useEffect(() => {
    async function loadInitialData() {
      try {
        const data = await getRecentUploads()
        setResumes(data)
        if (data && data.length > 0) {
          setSelectedResumeId(data[0].id)
        }
        
        const hist = await getInterviewHistory()
        setHistory(hist)
      } catch (err) {
        console.error(err)
      } finally {
        setLoadingResumes(false)
      }
    }
    loadInitialData()
  }, [])

  const handleStartInterview = async (e) => {
    e.preventDefault()
    if (!selectedResumeId || !jobTitle) return
    setStartingSession(true)
    setFinalReport(null)
    setSession(null)
    setCurrentQuestionIdx(0)
    setUserAnswer("")
    setCurrentCritique(null)
    try {
      const res = await startMockInterview(selectedResumeId, jobTitle, difficulty)
      if (res && !res.error) {
        setSession(res)
      }
    } catch (err) {
      console.error(err)
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
      }
    } catch (err) {
      console.error(err)
    } finally {
      setSubmittingAnswer(false)
    }
  }

  const handleNextQuestion = () => {
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
        // Refresh history logs
        const hist = await getInterviewHistory()
        setHistory(hist)
        // Exit session
        setSession(null)
      }
    } catch (err) {
      console.error(err)
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
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            AI Interview Prep
          </h1>
          <p className="text-gray-400 mt-2 text-lg">
            Train against custom technical, behavioral, and HR questions with instant AI feedback.
          </p>
        </div>

        {/* Resume Selector */}
        {!loadingResumes && resumes.length > 0 && !session && !finalReport && (
          <div className="flex items-center gap-3 bg-white/5 border border-white/10 p-3 rounded-2xl backdrop-blur-md">
            <FileText size={18} className="text-blue-400" />
            <select
              value={selectedResumeId}
              onChange={(e) => setSelectedResumeId(e.target.value)}
              className="bg-transparent text-gray-200 outline-none font-semibold text-sm cursor-pointer"
            >
              {resumes.map(r => (
                <option key={r.id} value={r.id} className="bg-slate-900 text-gray-200">
                  {r.name} ({r.score})
                </option>
              ))}
            </select>
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
                <h3 className="text-2xl font-bold text-gray-200">Session Setup</h3>
                
                <form onSubmit={handleStartInterview} className="space-y-5">
                  <div>
                    <label className="block text-sm text-gray-400 font-semibold mb-2">Target Job Title</label>
                    <input
                      type="text"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      required
                      placeholder="e.g. Full-Stack Developer"
                      className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-3.5 focus:border-blue-500 transition"
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

                  <button
                    type="submit"
                    disabled={startingSession}
                    className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:cursor-not-allowed font-semibold rounded-2xl text-white transition shadow-lg shadow-blue-500/20 cursor-pointer"
                  >
                    {startingSession ? (
                      <>
                        <RefreshCw className="animate-spin" size={16} /> Initializing Interview Panel...
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
              <div className="bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6">
                <h3 className="text-2xl font-bold text-gray-200 flex items-center gap-2">
                  <TrendingUp size={22} className="text-blue-400" /> Prep History
                </h3>
                
                {history.length === 0 ? (
                  <div className="text-center text-gray-500 text-sm py-12">
                    No past interview sessions found. Start a new practice session!
                  </div>
                ) : (
                  <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2">
                    {history.map(item => (
                      <div key={item.id} className="p-4 bg-white/5 border border-white/5 rounded-2xl flex justify-between items-center hover:border-white/10 transition">
                        <div>
                          <h5 className="font-bold text-sm text-gray-200">{item.job_title}</h5>
                          <span className="text-[10px] text-gray-400">{item.created_at} • {item.difficulty}</span>
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
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
              {/* Question & Answer Card */}
              <div className="lg:col-span-2 bg-white/5 border border-white/10 p-8 rounded-3xl backdrop-blur-md space-y-6">
                <div className="flex justify-between items-center border-b border-white/5 pb-4">
                  <span className="text-xs text-blue-400 font-bold uppercase tracking-wider">
                    Question {currentQuestionIdx + 1} of {session.questions.length}
                  </span>
                  <span className="text-[10px] px-2.5 py-1 bg-white/5 border border-white/5 text-gray-400 rounded-full font-semibold">
                    {session.questions[currentQuestionIdx].question_type}
                  </span>
                </div>

                <div className="space-y-4">
                  <h4 className="text-xl font-bold text-gray-200 flex items-start gap-2.5 leading-relaxed">
                    <HelpCircle size={22} className="text-blue-400 shrink-0 mt-1" />
                    {session.questions[currentQuestionIdx].question}
                  </h4>

                  <textarea
                    value={userAnswer}
                    onChange={(e) => setUserAnswer(e.target.value)}
                    disabled={currentCritique !== null || submittingAnswer}
                    rows={6}
                    placeholder="Type your response to this interview question here..."
                    className="w-full bg-slate-900 border border-white/10 text-gray-200 outline-none rounded-2xl px-5 py-4 focus:border-blue-500 transition text-sm leading-relaxed disabled:opacity-60"
                  />
                </div>

                <div className="flex gap-4">
                  {!currentCritique ? (
                    <button
                      onClick={handleSubmitAnswer}
                      disabled={submittingAnswer || !userAnswer.trim()}
                      className="w-full flex items-center justify-center gap-2 px-6 py-3.5 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-500/50 disabled:cursor-not-allowed font-semibold rounded-2xl text-white transition shadow-lg shadow-blue-500/20 cursor-pointer"
                    >
                      {submittingAnswer ? (
                        <>
                          <RefreshCw className="animate-spin" size={16} /> Evaluating Response...
                        </>
                      ) : (
                        <>
                          <Send size={16} /> Submit Answer
                        </>
                      )}
                    </button>
                  ) : (
                    <div className="w-full flex gap-4">
                      {currentQuestionIdx < session.questions.length - 1 ? (
                        <button
                          onClick={handleNextQuestion}
                          className="flex-1 py-3.5 bg-white/5 hover:bg-white/10 text-gray-200 border border-white/10 rounded-2xl transition font-semibold text-center cursor-pointer"
                        >
                          Next Question
                        </button>
                      ) : (
                        <button
                          onClick={handleCompleteInterview}
                          disabled={completing}
                          className="flex-1 py-3.5 bg-green-500 hover:bg-green-600 disabled:bg-green-600/50 font-semibold rounded-2xl text-white text-center transition shadow-lg shadow-green-500/20 cursor-pointer"
                        >
                          {completing ? "Grading Interview..." : "Complete & View Score"}
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>

              {/* Live Answer Critique Card */}
              <div>
                {!currentCritique ? (
                  <div className="bg-white/5 border border-white/10 border-dashed p-16 rounded-3xl text-center text-gray-400 text-sm backdrop-blur-md h-[400px] flex flex-col justify-center items-center">
                    <Award size={40} className="mb-4 text-gray-500" />
                    Submit your response to see detailed AI evaluation.
                  </div>
                ) : (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.98 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white/5 border border-white/10 p-6 rounded-3xl backdrop-blur-md space-y-6"
                  >
                    <div className="flex justify-between items-center border-b border-white/5 pb-4">
                      <h4 className="font-bold text-gray-200 flex items-center gap-1.5">
                        <Award size={18} className="text-blue-400" /> Answer Rating
                      </h4>
                      <span className="px-3.5 py-1.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-xl text-lg font-black">
                        {currentCritique.score}%
                      </span>
                    </div>

                    <div className="space-y-4">
                      <div>
                        <span className="text-xs text-purple-400 font-bold uppercase tracking-wider block mb-1.5">AI Evaluation Critique</span>
                        <p className="text-xs text-gray-300 leading-relaxed bg-white/5 border border-white/5 p-4 rounded-xl">
                          {currentCritique.ai_evaluation}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
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
