const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"

// Helper to construct authorization headers
function getAuthHeaders(isMultipart = false) {
  const token = localStorage.getItem("token")
  const headers = {}
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }
  if (!isMultipart) {
    headers["Content-Type"] = "application/json"
  }
  return headers
}

// Helper to handle responses and capture standard FastAPI HTTPException structures
async function handleResponse(response) {
  let data
  try {
    data = await response.json()
  } catch (err) {
    data = { error: "Failed to parse server response" }
  }

  if (!response.ok) {
    const errorMsg = data.detail || data.error || `Request failed with status ${response.status}`
    throw new Error(errorMsg)
  }
  return data
}

export async function signupUser(userData) {
  try {
    const response = await fetch(`${BASE_URL}/auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(userData)
    })
    return await handleResponse(response)
  } catch (error) {
    return { error: error.message }
  }
}

export async function loginUser(userData) {
  try {
    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(userData)
    })
    return await handleResponse(response)
  } catch (error) {
    return { error: error.message }
  }
}

export async function uploadResume(file) {
  try {
    const formData = new FormData()
    formData.append("file", file)

    const response = await fetch(`${BASE_URL}/resume/upload`, {
      method: "POST",
      headers: getAuthHeaders(true),
      body: formData
    })
    return await handleResponse(response)
  } catch (error) {
    return { error: error.message }
  }
}

export async function getRecentUploads() {
  try {
    const response = await fetch(`${BASE_URL}/resume/recent`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to fetch recent uploads:", error)
    return { error: error.message, data: [] }
  }
}

export async function getDashboardStats() {
  try {
    const response = await fetch(`${BASE_URL}/resume/stats`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to fetch dashboard stats:", error)
    return { avg_score: "0%", skills_found: "0", job_matches: "0", total_uploads: "0" }
  }
}

export async function getAnalyticsHistory() {
  try {
    const response = await fetch(`${BASE_URL}/resume/analytics`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to fetch analytics history:", error)
    return [{ name: "No Data", score: 0 }]
  }
}

export async function getParsedResume(id) {
  try {
    const response = await fetch(`${BASE_URL}/resume/parse/${id}`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to fetch parsed resume:", error)
    return null
  }
}

export async function getATSScoreBreakdown(id) {
  try {
    const response = await fetch(`${BASE_URL}/resume/ats/${id}`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to fetch ATS breakdown:", error)
    return null
  }
}

export async function analyzeResumeAI(resumeId, modelName = "gemini-2.5-flash", strictness = "standard") {
  try {
    const response = await fetch(`${BASE_URL}/ai/analyze`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ resume_id: resumeId, model_name: modelName, strictness })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to execute AI analysis:", error)
    return { error: error.message }
  }
}

export async function getAIFeedback(resumeId) {
  try {
    const response = await fetch(`${BASE_URL}/ai/feedback/${resumeId}`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to fetch stored AI feedback:", error)
    return null
  }
}

export async function rewriteSummary(resumeId, currentSummary = "") {
  try {
    const response = await fetch(`${BASE_URL}/ai/rewrite-summary`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ resume_id: resumeId, current_summary: currentSummary })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to rewrite resume summary:", error)
    return null
  }
}

export async function recommendSkills(skills) {
  try {
    const response = await fetch(`${BASE_URL}/ai/recommend-skills`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ skills })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to get technical recommendations:", error)
    return null
  }
}

export async function matchResumeJobs(resumeId, preferences = {}) {
  try {
    const response = await fetch(`${BASE_URL}/jobs/match`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        resume_id: resumeId,
        preferred_industries: preferences.preferred_industries || [],
        preferred_roles: preferences.preferred_roles || [],
        experience_level: preferences.experience_level || "",
        location_preference: preferences.location_preference || ""
      })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to run jobs matcher:", error)
    return { error: error.message }
  }
}

export async function getStoredJobMatches(resumeId) {
  try {
    const response = await fetch(`${BASE_URL}/jobs/recommend/${resumeId}`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.info("No stored job matches found for this resume (expected if matching hasn't been run):", error.message)
    return null
  }
}

export async function matchCustomJD(resumeId, customJDData) {
  try {
    const response = await fetch(`${BASE_URL}/jobs/match-custom`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        resume_id: resumeId,
        job_title: customJDData.job_title,
        job_description: customJDData.job_description,
        experience_level: customJDData.experience_level || "Intermediate",
        experience_years_required: parseInt(customJDData.experience_years_required) || 2,
        required_skills: customJDData.required_skills || [],
        industry: customJDData.industry || "Software Engineering",
        salary_range: customJDData.salary_range || "N/A"
      })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to match custom JD:", error)
    return { error: error.message }
  }
}

export async function getJobRoadmap(resumeId, jobTitle) {
  try {
    const response = await fetch(`${BASE_URL}/jobs/roadmap/${resumeId}/${encodeURIComponent(jobTitle)}`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to fetch job roadmap:", error)
    return null
  }
}

// Enterprise Resume Rewriter
export async function rewriteResumeSection(resumeId, section, originalText, focusArea = "ATS Optimization") {
  try {
    const response = await fetch(`${BASE_URL}/rewriter/rewrite`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ resume_id: resumeId, section, original_text: originalText, focus_area: focusArea })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to rewrite resume section:", error)
    return { error: error.message }
  }
}

// Enterprise Interview Prep
export async function startMockInterview(resumeId, jobTitle, difficulty = "Intermediate") {
  try {
    const response = await fetch(`${BASE_URL}/interviews/start`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ resume_id: resumeId, job_title: jobTitle, difficulty })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to start mock interview:", error)
    return { error: error.message }
  }
}

export async function submitInterviewAnswer(sessionId, questionIndex, userAnswer) {
  try {
    const response = await fetch(`${BASE_URL}/interviews/submit-answer`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ session_id: sessionId, question_index: questionIndex, user_answer: userAnswer })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to submit answer:", error)
    return { error: error.message }
  }
}

export async function completeMockInterview(sessionId) {
  try {
    const response = await fetch(`${BASE_URL}/interviews/complete`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ session_id: sessionId })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to complete interview:", error)
    return { error: error.message }
  }
}

export async function getInterviewHistory() {
  try {
    const response = await fetch(`${BASE_URL}/interviews/history`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to load interview history:", error)
    return []
  }
}

// Enterprise Live Jobs
export async function getLiveJobs(skills = "") {
  try {
    const response = await fetch(`${BASE_URL}/live-jobs/recommendations?skills=${encodeURIComponent(skills)}`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to load live jobs:", error)
    return []
  }
}

// Recruiter Dashboard
export async function searchCandidates(query = "") {
  try {
    const response = await fetch(`${BASE_URL}/recruiter/candidates?query=${encodeURIComponent(query)}`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed semantic candidate search:", error)
    return []
  }
}

export async function addCandidateToShortlist(resumeId, notes = "") {
  try {
    const response = await fetch(`${BASE_URL}/recruiter/shortlist/add`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ resume_id: resumeId, notes })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to add candidate to shortlist:", error)
    return { error: error.message }
  }
}

export async function getRecruiterShortlist() {
  try {
    const response = await fetch(`${BASE_URL}/recruiter/shortlist`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to fetch shortlists:", error)
    return { candidates: [] }
  }
}

export async function getRecruiterAnalytics() {
  try {
    const response = await fetch(`${BASE_URL}/recruiter/analytics`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to load recruiter analytics:", error)
    return { total_candidates: 0, avg_ats: "0%", top_skills: [] }
  }
}

export async function deleteResume(resumeId) {
  try {
    const response = await fetch(`${BASE_URL}/resume/${resumeId}`, {
      method: "DELETE",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to delete resume:", error)
    return { error: error.message }
  }
}

export async function renameResume(resumeId, newName) {
  try {
    const response = await fetch(`${BASE_URL}/resume/${resumeId}/rename`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({ name: newName })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to rename resume:", error)
    return { error: error.message }
  }
}

export async function downloadResume(resumeId, filename = "resume.pdf") {
  try {
    const token = localStorage.getItem("token")
    const headers = {}
    if (token) {
      headers["Authorization"] = `Bearer ${token}`
    }
    const response = await fetch(`${BASE_URL}/resume/${resumeId}/download`, {
      method: "GET",
      headers: headers
    })
    if (!response.ok) {
      throw new Error("Failed to download file")
    }
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
    return { success: true }
  } catch (error) {
    console.error("Failed to download resume:", error)
    return { error: error.message }
  }
}

export async function reanalyzeResume(resumeId) {
  try {
    const response = await fetch(`${BASE_URL}/resume/${resumeId}/reanalyze`, {
      method: "POST",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to reanalyze resume:", error)
    return { error: error.message }
  }
}

export async function multimodalAnalyzeResume(resumeId) {
  try {
    const response = await fetch(`${BASE_URL}/resume/${resumeId}/multimodal-analyze`, {
      method: "POST",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed visual analysis:", error)
    return { error: error.message }
  }
}

export async function changePassword(currentPassword, newPassword) {
  try {
    const response = await fetch(`${BASE_URL}/auth/change-password`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to change password:", error)
    return { error: error.message }
  }
}

export async function analyzeResume(id) {
  try {
    const response = await fetch(`${BASE_URL}/resume/${id}/analyze`, {
      method: "POST",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to analyze resume:", error)
    return { error: error.message }
  }
}

export async function postRecruiterJob(jobData) {
  try {
    const response = await fetch(`${BASE_URL}/recruiter/jobs`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(jobData)
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to post recruiter job:", error)
    return { error: error.message }
  }
}

export async function getRecruiterJobs() {
  try {
    const response = await fetch(`${BASE_URL}/recruiter/jobs`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to list recruiter jobs:", error)
    return []
  }
}

export async function listResumes() {
  try {
    const response = await fetch(`${BASE_URL}/resume/list`, {
      method: "GET",
      headers: getAuthHeaders()
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to list resumes:", error)
    return []
  }
}

export async function refreshToken(tokenPayload) {
  try {
    const response = await fetch(`${BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(tokenPayload)
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to refresh token:", error)
    return { error: error.message }
  }
}

export async function forgotPassword(emailData) {
  try {
    const response = await fetch(`${BASE_URL}/auth/forgot-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(emailData)
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to request password reset:", error)
    return { error: error.message }
  }
}

export async function resetPassword(resetData) {
  try {
    const response = await fetch(`${BASE_URL}/auth/reset-password`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(resetData)
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to reset password:", error)
    return { error: error.message }
  }
}

export async function requestEmailVerification(emailData) {
  try {
    const response = await fetch(`${BASE_URL}/auth/request-email-verification`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(emailData)
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to request email verification:", error)
    return { error: error.message }
  }
}

export async function verifyEmail(verifyData) {
  try {
    const response = await fetch(`${BASE_URL}/auth/verify-email`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(verifyData)
    })
    return await handleResponse(response)
  } catch (error) {
    console.error("Failed to verify email:", error)
    return { error: error.message }
  }
}

