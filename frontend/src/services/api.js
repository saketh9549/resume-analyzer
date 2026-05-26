const BASE_URL = "http://127.0.0.1:8000"

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
    return []
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
