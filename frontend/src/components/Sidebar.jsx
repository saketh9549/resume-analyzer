import { Link } from "react-router-dom"

function Sidebar() {

  return (
    <div className="w-64 bg-slate-900 p-6">

      <h1 className="text-3xl font-bold mb-10">
        ResumeAI
      </h1>

      <ul className="space-y-4">

        <li>
          <Link
            to="/"
            className="hover:text-blue-400"
          >
            Dashboard
          </Link>
        </li>

        <li>
          <Link
            to="/upload"
            className="hover:text-blue-400"
          >
            Upload Resume
          </Link>
        </li>

        <li>
          <Link
            to="/analytics"
            className="hover:text-blue-400"
          >
            Analytics
          </Link>
        </li>

      </ul>

    </div>
  )
}

export default Sidebar