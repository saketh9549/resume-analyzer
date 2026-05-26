import { useState } from "react"
import { Link } from "react-router-dom"

function Navbar({ darkMode, setDarkMode }) {

  const [dropdownOpen, setDropdownOpen] = useState(false)
  
  let user = null
  try {
    const rawUser = localStorage.getItem("user")
    if (rawUser) {
      user = JSON.parse(rawUser)
    }
  } catch (err) {
    console.error("Failed to parse user details from local storage:", err)
  }

  // Check actual auth token dynamically
  const isLoggedIn = !!localStorage.getItem("token")

  return (

    <div className="flex items-center justify-between mb-10">

      {/* Left */}
      <div>

        <h1 className="text-5xl font-bold">
          Dashboard
        </h1>

        <p className="text-gray-400 mt-2 text-lg">
          Welcome back, {user?.name || "User"}
        </p>


      </div>

      {/* Right */}
      <div className="flex items-center gap-6">

        {/* Search */}
        <input
          type="text"
          placeholder="Search..."
          className="
            bg-white/5
            backdrop-blur-md
            px-5
            py-4
            rounded-2xl
            outline-none
            border
            border-white/10
            focus:border-blue-500
            transition
            w-80
          "
        />
        <button
            onClick={() => setDarkMode(!darkMode)}
            className="
                bg-white/5
                backdrop-blur-lg
                p-4
                rounded-2xl
                hover:bg-white/10
                transition
            "
            >
            {darkMode ? "☀️" : "🌙"}
        </button>
        {/* Notification */}
        <button
          className="
            bg-white/5
            backdrop-blur-lg
            p-4
            rounded-2xl
            hover:bg-white/10
            transition
          "
        >
          🔔
        </button>

        {/* AUTH */}
        {
          isLoggedIn ? (

            <div className="relative">

              {/* Profile Button */}
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="
                  flex
                  items-center
                  gap-4
                  bg-white/5
                  hover:bg-white/10
                  px-4
                  py-3
                  rounded-2xl
                  transition
                "
              >

                {/* Avatar */}
                <div
                  className="
                    w-14
                    h-14
                    rounded-full
                    bg-blue-500
                    flex
                    items-center
                    justify-center
                    font-bold
                    text-xl
                  "
                >
                  S
                </div>

                {/* Info */}
                <div className="text-left">

                  <p className="font-semibold text-lg">
                    {user?.name}
                  </p>

                  <p className="text-gray-400 text-sm">
                    Authenticated User
                  </p>

                </div>

              </button>

              {/* Dropdown */}
              {
                dropdownOpen && (

                  <div
                    className="
                      absolute
                      right-0
                      mt-4
                      w-64
                      bg-slate-900/95
                      backdrop-blur-lg
                      border
                      border-white/10
                      rounded-2xl
                      p-3
                      shadow-2xl
                      z-50
                    "
                  >

                    <button
                      className="
                        w-full
                        text-left
                        px-4
                        py-3
                        rounded-xl
                        hover:bg-white/10
                        transition
                      "
                    >
                      My Profile
                    </button>

                    <button
                      className="
                        w-full
                        text-left
                        px-4
                        py-3
                        rounded-xl
                        hover:bg-white/10
                        transition
                      "
                    >
                      Settings
                    </button>

                    <button className="
                        w-full
                        text-left
                        px-4
                        py-3
                        rounded-xl
                        hover:bg-red-500/20
                        text-red-400
                        transition
                      "
                        onClick={() => {

                            localStorage.removeItem("token")
                            localStorage.removeItem("user")

                            window.location.href = "/login"
                        }}
                        >
                        Logout
                    </button>

                  </div>

                )
              }

            </div>

          ) : (

            <div className="flex gap-4">

              <Link
                to="/login"
                className="
                  px-5
                  py-3
                  rounded-2xl
                  border
                  border-white/10
                  hover:bg-white/10
                  transition
                "
              >
                Login
              </Link>

              <Link
                to="/signup"
                className="
                  px-5
                  py-3
                  rounded-2xl
                  bg-blue-500
                  hover:bg-blue-600
                  transition
                "
              >
                Sign Up
              </Link>

            </div>

          )
        }

      </div>

    </div>

  )
}

export default Navbar