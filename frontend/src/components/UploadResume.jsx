import { useState } from "react"
import ScoreGauge from "./ScoreGauge"

function UploadResume() {

  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dragging, setDragging] = useState(false)

  function handleFileChange(event) {

    const selectedFile = event.target.files[0]

    setLoading(true)

    setTimeout(() => {

      setFile(selectedFile)

      setLoading(false)

    }, 2500)
  }

  function handleDragOver(event) {
    event.preventDefault()
    setDragging(true)
  }

  function handleDragLeave() {
    setDragging(false)
  }

  function handleDrop(event) {

    event.preventDefault()

    setDragging(false)

    const droppedFile = event.dataTransfer.files[0]

    setLoading(true)

    setTimeout(() => {

      setFile(droppedFile)

      setLoading(false)

    }, 2500)
  }

  return (

    <div>

      <h1 className="text-5xl font-bold mb-8">
        Upload Resume
      </h1>

      {/* STEP BAR */}
      <div className="flex items-center gap-6 mb-10">

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
            1
          </div>

          <p>Upload</p>

        </div>

        <div className="w-20 h-1 bg-blue-500 rounded" />

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center">
            2
          </div>

          <p>Analyze</p>

        </div>

        <div className="w-20 h-1 bg-slate-700 rounded" />

        <div className="flex items-center gap-3">

          <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center">
            3
          </div>

          <p>Improve</p>

        </div>

      </div>

      {/* BEFORE UPLOAD */}
      {
        !file && !loading && (

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`
              p-20
              rounded-3xl
              border-2
              border-dashed
              text-center
              transition-all
              duration-300
              cursor-pointer
              max-w-3xl
              mx-auto

              ${dragging
                ? "border-blue-500 bg-blue-500/10 scale-105"
                : "border-white/10 bg-white/5 backdrop-blur-lg"
              }
            `}
          >

            <div className="text-7xl mb-8">
              📄
            </div>

            <h2 className="text-5xl font-bold mb-6">
              Drag & Drop Resume
            </h2>

            <p className="text-gray-400 text-xl mb-8">
              Upload PDF, DOC, or DOCX files
            </p>

            <label
              className="
                inline-block
                bg-blue-500
                hover:bg-blue-600
                px-8
                py-4
                rounded-2xl
                transition
                cursor-pointer
                font-semibold
                text-lg
              "
            >

              Choose File

              <input
                type="file"
                accept=".pdf,.doc,.docx"
                onChange={handleFileChange}
                className="hidden"
              />

            </label>

          </div>

        )
      }

      {/* LOADING */}
      {
        loading && (

          <div
            className="
              mt-10
              bg-white/5
              backdrop-blur-lg
              border
              border-white/10
              p-16
              rounded-3xl
              text-center
              max-w-4xl
              mx-auto
            "
          >

            <div className="space-y-4">

                <div className="h-6 bg-slate-700 rounded animate-pulse" />

                <div className="h-6 bg-slate-700 rounded animate-pulse" />

                <div className="h-32 bg-slate-700 rounded-2xl animate-pulse" />

                </div>

            <h2 className="text-4xl font-bold mt-10 mb-6">
              AI is analyzing your resume
            </h2>

            <p className="text-gray-400 text-lg">
              Extracting skills, calculating ATS score,
              and generating intelligent feedback...
            </p>

          </div>

        )
      }

      {/* AFTER UPLOAD */}
      {
        file && !loading && (

          <div className="grid grid-cols-2 gap-8 mt-10">

            {/* LEFT SIDE */}
            <div>

              {/* AI FEEDBACK */}
              <div
                className="
                  bg-white/5
                  backdrop-blur-lg
                  border
                  border-white/10
                  p-8
                  rounded-3xl
                "
              >

                <div className="flex items-center justify-between mb-6">

                  <h2 className="text-2xl font-bold">
                    AI Resume Feedback
                  </h2>

                  <span
                    className="
                      bg-green-500/20
                      text-green-400
                      px-4
                      py-2
                      rounded-xl
                      text-sm
                    "
                  >
                    Analysis Complete
                  </span>

                </div>

                {/* FEEDBACK CARDS */}
                <div className="grid grid-cols-2 gap-6">

                  <div
                    className="
                      bg-slate-900/70
                      p-6
                      rounded-2xl
                    "
                  >

                    <h3 className="text-lg font-semibold mb-3">
                      ATS Score
                    </h3>

                    <p className="text-5xl font-bold text-blue-400">
                      82%
                    </p>

                  </div>

                  <div
                    className="
                      bg-slate-900/70
                      p-6
                      rounded-2xl
                    "
                  >

                    <h3 className="text-lg font-semibold mb-3">
                      Missing Skills
                    </h3>

                    <p className="text-gray-300">
                      Docker, Kubernetes, AWS
                    </p>

                  </div>

                </div>
            <ScoreGauge />
                {/* SUGGESTIONS */}
                <div
                  className="
                    mt-6
                    bg-slate-900/70
                    p-5
                    rounded-2xl
                  "
                >

                  <h3 className="text-xl font-semibold mb-4">
                    Suggestions
                  </h3>

                  <ul className="space-y-3 text-gray-300">

                    <li>
                      • Add more quantified achievements
                    </li>

                    <li>
                      • Improve project descriptions
                    </li>

                    <li>
                      • Include cloud technologies
                    </li>

                    <li>
                      • Optimize resume keywords for ATS
                    </li>

                  </ul>

                </div>

              </div>

            </div>

            {/* RIGHT SIDE */}
            <div
              className="
                bg-white/5
                backdrop-blur-lg
                border
                border-white/10
                rounded-3xl
                p-6
                min-h-[700px]
              "
            >

              <div className="flex items-center justify-between mb-6">

                <h2 className="text-2xl font-bold">
                  Resume Preview
                </h2>

                <span
                  className="
                    bg-blue-500/20
                    text-blue-400
                    px-4
                    py-2
                    rounded-xl
                    text-sm
                  "
                >
                  Live Preview
                </span>

              </div>

              <div
                className="
                  h-[600px]
                  bg-slate-900/70
                  rounded-2xl
                  flex
                  items-center
                  justify-center
                  border
                  border-white/10
                  overflow-hidden
                "
              >

                {
                  file.type === "application/pdf" ? (

                    <iframe
                      src={URL.createObjectURL(file)}
                      title="Resume Preview"
                      className="
                        w-full
                        h-full
                        rounded-2xl
                      "
                    />

                  ) : (

                    <div className="text-center">

                      <div className="text-7xl mb-6">
                        📄
                      </div>

                      <h3 className="text-2xl font-semibold mb-4">
                        {file.name}
                      </h3>

                      <p className="text-gray-400">
                        Preview available only for PDF files
                      </p>

                    </div>

                  )
                }

              </div>

            </div>

          </div>

        )
      }

    </div>

  )
}

export default UploadResume