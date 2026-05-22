const uploads = [
  {
    name: "Resume_Developer.pdf",
    score: "82%",
    date: "2026-05-18"
  },
  {
    name: "Resume_DataScience.pdf",
    score: "76%",
    date: "2026-05-17"
  },
  {
    name: "Resume_Designer.pdf",
    score: "91%",
    date: "2026-05-15"
  }
]

function RecentUploads() {

  return (

    <div className="bg-slate-900 p-6 rounded-2xl mt-10">

      <div className="flex items-center justify-between mb-6">

        <h2 className="text-2xl font-bold">
          Recent Uploads
        </h2>

        <button
          className="
            bg-blue-500
            px-4
            py-2
            rounded-xl
            hover:bg-blue-600
            transition
          "
        >
          View All
        </button>

      </div>

      {/* Table Header */}
      <div
        className="
          grid
          grid-cols-3
          text-gray-400
          border-b
          border-slate-700
          pb-3
        "
      >

        <p>Resume</p>
        <p>ATS Score</p>
        <p>Date</p>

      </div>

      {/* Table Rows */}
      <div className="mt-4 space-y-4">

        {
          uploads.map((upload, index) => (

            <div
              key={index}
              className="
                grid
                grid-cols-3
                bg-slate-800
                p-4
                rounded-xl
                hover:bg-slate-700
                transition
              "
            >

              <p>{upload.name}</p>

              <p className="text-green-400">
                {upload.score}
              </p>

              <p>{upload.date}</p>

            </div>

          ))
        }

      </div>

    </div>

  )
}

export default RecentUploads