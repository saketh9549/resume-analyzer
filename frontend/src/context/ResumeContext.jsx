import React, { createContext, useState, useEffect, useContext } from 'react'
import { listResumes } from '../services/resumeApi'

const ResumeContext = createContext()

export const ResumeProvider = ({ children }) => {
  const [resumes, setResumes] = useState([])
  const [activeResume, setActiveResume] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchResumes = async () => {
    setLoading(true)
    try {
      const data = await listResumes()
      if (Array.isArray(data)) {
        setResumes(data)
        
        // Restore active resume from localStorage if present
        const savedId = localStorage.getItem('activeResumeId')
        if (savedId) {
          const matched = data.find(r => r.id === savedId)
          if (matched) {
            setActiveResume(matched)
            setLoading(false)
            return data
          }
        }
        
        if (data.length > 0) {
          setActiveResume(data[0])
          localStorage.setItem('activeResumeId', data[0].id)
        } else {
          setActiveResume(null)
          localStorage.removeItem('activeResumeId')
        }
        return data
      }
      return []
    } catch (err) {
      console.error('Failed to load resumes into context:', err)
      return []
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Only load if authenticated
    if (localStorage.getItem('token')) {
      fetchResumes()
    }
  }, [])

  const selectActiveResume = (resume) => {
    setActiveResume(resume)
    if (resume && resume.id) {
      localStorage.setItem('activeResumeId', resume.id)
    } else {
      localStorage.removeItem('activeResumeId')
    }
  }

  return (
    <ResumeContext.Provider value={{
      resumes,
      activeResume,
      setActiveResume: selectActiveResume,
      loading,
      refreshResumes: fetchResumes
    }}>
      {children}
    </ResumeContext.Provider>
  )
}

export const useResume = () => {
  const context = useContext(ResumeContext)
  if (!context) {
    throw new Error('useResume must be used within a ResumeProvider')
  }
  return context
}
