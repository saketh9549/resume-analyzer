import { useState } from "react"

function UploadResume() {

  const [file, setFile] = useState(null)

  function handleFileChange(event) {
    setFile(event.target.files[0])
  }

  return (
    <div>

      <h1 className="text-5xl font-bold mb-8">
        Upload Resume
      </h1>

      {/* Upload Box */}
      <div className="bg-slate-900 p-10 rounded-2xl border-2 border-dashed border-slate-700 text-center">

        <p className="text-xl mb-6 text-gray-400">
          Drag and drop your resume here
        </p>

        <input
          type="file"
          accept=".pdf,.doc,.docx"
          onChange={handleFileChange}
          className="mb-4"
        />

        {
          file && (
            <div className="mt-4">

              <p className="text-green-400">
                File Selected:
              </p>

              <p className="mt-2 text-lg">
                {file.name}
              </p>

            </div>
          )
        }

      </div>

    </div>
  )
}

export default UploadResume