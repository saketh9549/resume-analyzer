import { Link, useNavigate } from "react-router-dom"
import { useState } from "react"
import { signupUser } from "../services/api"

function Signup() {

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const navigate = useNavigate()

  async function handleSignup() {
    if (!name.strip && !name.trim()) {
      alert("Please enter your name.")
      return
    }
    if (!email.includes("@")) {
      alert("Please enter a valid email address.")
      return
    }
    if (password.length < 6) {
      alert("Password must be at least 6 characters.")
      return
    }

    const response = await signupUser({
      name,
      email,
      password
    })

    console.log(response)

    if (response.error) {
      alert(response.error)
    } else {
      alert(response.message || "Account created successfully!")
      navigate("/login")
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
          Create Account
        </h1>

        <p className="text-gray-400 mb-10">
          Join ResumeAI platform
        </p>

        {/* Name */}
        <div className="mb-6">

          <label className="block mb-2 text-gray-300">
            Full Name
          </label>

          <input
            type="text"
            placeholder="Enter your full name"
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
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

        </div>

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
            placeholder="Create password"
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
          onClick={handleSignup}
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
          Create Account
        </button>

        {/* Footer */}
        <p className="text-gray-400 text-center">

          Already have an account?{" "}

          <Link
            to="/login"
            className="text-blue-400 hover:text-blue-300"
          >
            Login
          </Link>

        </p>

      </div>

    </div>

  )
}

export default Signup