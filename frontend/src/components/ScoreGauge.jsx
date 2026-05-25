import { CircularProgressbar } from "react-circular-progressbar"
import "react-circular-progressbar/dist/styles.css"

function ScoreGauge() {

  return (

    <div
      className="
        bg-white/5
        backdrop-blur-lg
        border
        border-white/10
        rounded-3xl
        p-8
      "
    >

      <h2 className="text-2xl font-bold mb-8">
        ATS Match Score
      </h2>

      <div className="w-48 mx-auto">

        <CircularProgressbar
          value={82}
          text="82%"
        />

      </div>

    </div>

  )
}

export default ScoreGauge