import { Link } from "react-router-dom"
import { useState } from "react"
import { loginUser } from "../services/api"
import { useNavigate } from "react-router-dom"

function Login() {

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
    const navigate = useNavigate()
  async function handleLogin() {

    const response = await loginUser({
      email,
      password
    })

    console.log(response)

    if (response.access_token) {

      localStorage.setItem(
        "token",
        response.access_token
      )

      localStorage.setItem(
        "user",
        JSON.stringify(response.user)
      )

      navigate("/")

    } else {

      alert(response.error)
    }
  }

  return (

    <div
      className="
        min-h-screen
        flex
        items-center
        justify-center
        bg-gradient-to-br
        from-slate-950
        via-slate-900
        to-slate-950
        text-white
      "
    >

      <div
        className="
          w-full
          max-w-md
          bg-white/5
          backdrop-blur-lg
          border
          border-white/10
          p-10
          rounded-3xl
          shadow-2xl
        "
      >

        <h1 className="text-5xl font-bold mb-3">
          Welcome Back
        </h1>

        <p className="text-gray-400 mb-10">
          Login to your ResumeAI account
        </p>

        {/* Email */}
        <div className="mb-6">

          <label className="block mb-2 text-gray-300">
            Email
          </label>

          <input
            type="email"
            placeholder="Enter your email"
            className="
              w-full
              bg-slate-900/70
              border
              border-white/10
              rounded-2xl
              px-4
              py-4
              outline-none
              focus:border-blue-500
              transition
            "
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

        </div>

        {/* Password */}
        <div className="mb-8">

          <label className="block mb-2 text-gray-300">
            Password
          </label>

          <input
            type="password"
            placeholder="Enter your password"
            className="
              w-full
              bg-slate-900/70
              border
              border-white/10
              rounded-2xl
              px-4
              py-4
              outline-none
              focus:border-blue-500
              transition
            "
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

        </div>

        {/* Button */}
        <button
          onClick={handleLogin}
          className="
            w-full
            bg-blue-500
            hover:bg-blue-600
            py-4
            rounded-2xl
            font-semibold
            transition
            mb-6
          "
        >
          Login
        </button>

        {/* Footer */}
        <p className="text-gray-400 text-center">

          Don’t have an account?{" "}

          <Link
            to="/signup"
            className="text-blue-400 hover:text-blue-300"
          >
            Create Account
          </Link>

        </p>

      </div>

    </div>

  )
}

export default Login