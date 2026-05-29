import { BASE_URL } from "./api"

const activeRequests = new Map()

async function dedupedFetch(url, options = {}) {
  const method = options.method || "GET"
  if (method !== "GET") {
    return fetch(url, options)
  }
  
  const token = localStorage.getItem("token") || ""
  const key = `${url}_${token}`
  
  if (activeRequests.has(key)) {
    const cachedResponse = await activeRequests.get(key)
    return cachedResponse.clone()
  }
  
  const promise = fetch(url, options).catch(err => {
    activeRequests.delete(key)
    throw err
  })
  
  activeRequests.set(key, promise)
  
  try {
    const response = await promise
    activeRequests.delete(key)
    return response.clone()
  } catch (err) {
    activeRequests.delete(key)
    throw err
  }
}


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

export async function uploadResume(file) {
  const formData = new FormData()
  formData.append("file", file)

  const response = await dedupedFetch(`${BASE_URL}/resume/upload`, {
    method: "POST",
    headers: getAuthHeaders(true),
    body: formData
  })
  return await handleResponse(response)
}

export async function listResumes() {
  const response = await dedupedFetch(`${BASE_URL}/resume/list`, {
    method: "GET",
    headers: getAuthHeaders()
  })
  return await handleResponse(response)
}

export function getPreviewUrl(id) {
  const token = localStorage.getItem("token") || ""
  return `${BASE_URL}/resume/preview/${id}?token=${encodeURIComponent(token)}`
}

export async function downloadResumeFile(id, filename = "resume.pdf") {
  const token = localStorage.getItem("token")
  const headers = {}
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }
  const response = await dedupedFetch(`${BASE_URL}/resume/download/${id}`, {
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
}

export async function deleteResume(id) {
  const response = await dedupedFetch(`${BASE_URL}/resume/${id}`, {
    method: "DELETE",
    headers: getAuthHeaders()
  })
  return await handleResponse(response)
}

export async function renameResume(id, newName) {
  const response = await dedupedFetch(`${BASE_URL}/resume/rename/${id}`, {
    method: "PATCH",
    headers: getAuthHeaders(),
    body: JSON.stringify({ name: newName })
  })
  return await handleResponse(response)
}

export async function analyzeResume(id) {
  const response = await dedupedFetch(`${BASE_URL}/resume/${id}/analyze`, {
    method: "POST",
    headers: getAuthHeaders()
  })
  return await handleResponse(response)
}

export async function getAnalysisResults(id) {
  const response = await dedupedFetch(`${BASE_URL}/resume/${id}/analysis-results`, {
    method: "GET",
    headers: getAuthHeaders()
  })
  return await handleResponse(response)
}