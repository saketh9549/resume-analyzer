function Navbar() {
  return (

    <div className="flex items-center justify-between mb-10">

      {/* Left Side */}
      <div>

        <h1 className="text-4xl font-bold">
          Dashboard
        </h1>

        <p className="text-gray-400 mt-2">
          Welcome back, Saketh
        </p>

      </div>

      {/* Right Side */}
      <div className="flex items-center gap-6">

        {/* Search */}
        <input
          type="text"
          placeholder="Search..."
          className="
            bg-white/5
            backdrop-blur-md
            px-4
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

        {/* Notification */}
        <button
          className="
            bg-slate-900
            p-3
            rounded-xl
            hover:bg-slate-800
            transition
          "
        >
          🔔
        </button>

        {/* Profile */}
        <div className="flex items-center gap-3">

          <div
            className="
              w-12
              h-12
              rounded-full
              bg-blue-500
              flex
              items-center
              justify-center
              font-bold
              text-lg
            "
          >
            S
          </div>

          <div>

            <p className="font-semibold">
              Saketh
            </p>

            <p className="text-sm text-gray-400">
              Intern
            </p>

          </div>

        </div>

      </div>

    </div>

  )
}

export default Navbar