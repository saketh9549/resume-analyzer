import UploadResume from "../components/UploadResume"
import { useState } from "react"
import { uploadResume } from "../services/api"


function Upload() {
    
    const [file, setFile] = useState(null)
    const handleFileChange = async (e) => {

  const selectedFile = e.target.files[0]

  if (!selectedFile) return

  setFile(selectedFile)

  try {

    const response = await uploadResume(
      selectedFile
    )

    console.log(response)

    alert(response.message)

  } catch (error) {

    console.log(error)

    alert("Upload failed")
  }
}
  return (
    <UploadResume />
  )
}

export default Upload