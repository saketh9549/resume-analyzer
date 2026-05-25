const BASE_URL = "http://127.0.0.1:8000"

export async function signupUser(userData) {

  const response = await fetch(
    `${BASE_URL}/auth/signup`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify(userData)
    }
  )

  return response.json()
}

export async function loginUser(userData) {

  const response = await fetch(
    `${BASE_URL}/auth/login`,
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify(userData)
    }
  )

  return response.json()
}

export async function uploadResume(file) {

  const formData = new FormData()

  formData.append("file", file)

  const response = await fetch(
    "http://127.0.0.1:8000/resume/upload",
    {
      method: "POST",
      body: formData
    }
  )

  return response.json()
}