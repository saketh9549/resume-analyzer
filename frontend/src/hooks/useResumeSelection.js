import { useResume } from '../context/ResumeContext'

export const useResumeSelection = () => {
  const { resumes, activeResume, setActiveResume, loading, refreshResumes } = useResume()
  
  return {
    resumes,
    activeResume,
    setActiveResume,
    loading,
    refreshResumes
  }
}

export default useResumeSelection
