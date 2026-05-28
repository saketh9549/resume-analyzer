import { useState, useEffect } from "react"
import { Link, useNavigate, useLocation } from "react-router-dom"

function Navbar() {
  const navigate = useNavigate()
  const location = useLocation()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const [user, setUser] = useState(() => {
    try {
      const rawUser = localStorage.getItem("user")
      return rawUser ? JSON.parse(rawUser) : null
    } catch {
      return null
    }
  })

  // Synchronize display name state if changed inside profile page edit inputs
  useEffect(() => {
    function handleStorageChange() {
      try {
        const rawUser = localStorage.getItem("user")
        if (rawUser) {
          setUser(JSON.parse(rawUser))
        }
      } catch (err) {
        console.error("Failed to parse user details:", err)
      }
    }
    // Listen to storage changes (dispatched locally when name edits complete)
    window.addEventListener("storage", handleStorageChange)
    return () => window.removeEventListener("storage", handleStorageChange)
  }, [])

  // Check actual auth token dynamically
  const isLoggedIn = !!localStorage.getItem("token")

  function handleLogout() {
    localStorage.removeItem("token")
    localStorage.removeItem("user")
    navigate("/login")
  }

  // Derive page heading title from route location
  let pageTitle = "Dashboard"
  if (location.pathname === "/upload") {
    pageTitle = "Upload Resume"
  } else if (location.pathname === "/analytics") {
    pageTitle = "Analytics & Reports"
  } else if (location.pathname === "/profile") {
    pageTitle = "My Profile"
  } else if (location.pathname === "/settings") {
    pageTitle = "Settings"
  }

  const initial = user?.name ? user.name.charAt(0).toUpperCase() : "U"

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
      {/* PAGE HEADER */}
      <div>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight">
          {pageTitle}
        </h1>
        <p className="text-gray-400 mt-1 text-sm sm:text-base">
          Welcome back, {user?.name || "Candidate"}
        </p>
      </div>

      {/* RIGHT SIDE OPTIONS */}
      <div className="flex items-center gap-4 self-end sm:self-auto w-full sm:w-auto justify-end">
        {/* Search */}
        <input
          type="text"
          placeholder="Search..."
          className="
            hidden md:block
            bg-white/5
            backdrop-blur-md
            px-5
            py-3
            rounded-2xl
            outline-none
            border
            border-white/10
            focus:border-blue-500
            transition
            w-64
          "
        />

        {/* Notification Button */}
        <button
          className="
            bg-white/5
            backdrop-blur-lg
            p-3.5
            rounded-2xl
            hover:bg-white/10
            transition
            border border-white/5
          "
        >
          🔔
        </button>

        {/* AUTH DROPDOWN OR REGISTRATION LOGS */}
        {isLoggedIn ? (
          <div className="relative">
            {/* Profile Trigger Button */}
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="
                flex
                items-center
                gap-3
                bg-white/5
                hover:bg-white/10
                px-4
                py-2.5
                rounded-2xl
                transition
                border border-white/5
              "
            >
              {/* Avatar circle */}
              <div
                className="
                  w-10
                  h-10
                  rounded-full
                  bg-blue-600
                  flex
                  items-center
                  justify-center
                  font-bold
                  text-lg
                  shadow-md
                "
              >
                {initial}
              </div>

              {/* User text */}
              <div className="text-left hidden sm:block">
                <p className="font-semibold text-sm leading-tight">
                  {user?.name || "Account"}
                </p>
                <p className="text-gray-400 text-xs mt-0.5">
                  {user?.role ? (user.role.charAt(0).toUpperCase() + user.role.slice(1)) : "Candidate"}
                </p>
              </div>
            </button>

            {/* Dropdown Box */}
            {dropdownOpen && (
              <div
                className="
                  absolute
                  right-0
                  mt-3
                  w-56
                  bg-slate-900/95
                  backdrop-blur-xl
                  border
                  border-white/10
                  rounded-2xl
                  p-2
                  shadow-2xl
                  z-50
                "
              >
                <button
                  onClick={() => {
                    setDropdownOpen(false)
                    navigate("/profile")
                  }}
                  className="
                    w-full
                    text-left
                    px-4
                    py-2.5
                    text-sm
                    rounded-xl
                    hover:bg-white/10
                    transition
                    font-medium
                  "
                >
                  My Profile
                </button>

                <button
                  onClick={() => {
                    setDropdownOpen(false)
                    navigate("/settings")
                  }}
                  className="
                    w-full
                    text-left
                    px-4
                    py-2.5
                    text-sm
                    rounded-xl
                    hover:bg-white/10
                    transition
                    font-medium
                  "
                >
                  Settings
                </button>

                <div className="border-t border-white/5 my-1" />

                <button
                  onClick={() => {
                    setDropdownOpen(false)
                    handleLogout()
                  }}
                  className="
                    w-full
                    text-left
                    px-4
                    py-2.5
                    text-sm
                    rounded-xl
                    hover:bg-red-500/20
                    text-red-400
                    transition
                    font-medium
                  "
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="flex gap-2">
            <Link
              to="/login"
              className="
                px-5
                py-2.5
                text-sm
                rounded-2xl
                border
                border-white/10
                hover:bg-white/10
                transition
                font-semibold
              "
            >
              Login
            </Link>

            <Link
              to="/signup"
              className="
                px-5
                py-2.5
                text-sm
                rounded-2xl
                bg-blue-500
                hover:bg-blue-600
                transition
                font-semibold
               text-white
              "
            >
              Sign Up
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}

export default Navbar