import React, { createContext, useState, useEffect, useContext } from 'react'

const CareerPreferenceContext = createContext()
import { BASE_URL } from '../services/api'

function getAuthHeaders() {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  }
}

export const CareerPreferenceProvider = ({ children }) => {
  const [preferences, setPreferences] = useState({
    preferred_roles: [],
    preferred_technologies: [],
    experience_level: '',
    preferred_industries: [],
    expected_salary: '',
    remote_preference: '',
    location_preference: ''
  })
  const [loading, setLoading] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  const fetchPreferences = async () => {
    if (!localStorage.getItem('token')) return
    setLoading(true)
    try {
      const response = await fetch(`${BASE_URL}/auth/preferences`, {
        headers: getAuthHeaders()
      })
      if (response.ok) {
        const data = await response.json()
        setPreferences({
          preferred_roles: data.preferred_roles || [],
          preferred_technologies: data.preferred_technologies || [],
          experience_level: data.experience_level || '',
          preferred_industries: data.preferred_industries || [],
          expected_salary: data.expected_salary || '',
          remote_preference: data.remote_preference || '',
          location_preference: data.location_preference || ''
        })
      }
    } catch (err) {
      console.error('Failed to fetch preferences:', err)
    } finally {
      setLoading(false)
    }
  }

  const updatePreferences = async (newPrefs) => {
    setLoading(true)
    setSaveSuccess(false)
    try {
      const response = await fetch(`${BASE_URL}/auth/preferences`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(newPrefs)
      })
      if (response.ok) {
        const data = await response.json()
        setPreferences(data.preferences)
        setSaveSuccess(true)
        setTimeout(() => setSaveSuccess(false), 3000)
        return { success: true }
      }
      return { error: 'Failed to update preferences on server' }
    } catch (err) {
      console.error('Failed to update preferences:', err)
      return { error: err.message }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (localStorage.getItem('token')) {
      fetchPreferences()
    }
  }, [])

  return (
    <CareerPreferenceContext.Provider value={{
      preferences,
      updatePreferences,
      loading,
      saveSuccess,
      refreshPreferences: fetchPreferences
    }}>
      {children}
    </CareerPreferenceContext.Provider>
  )
}

export const useCareerPreferences = () => {
  const context = useContext(CareerPreferenceContext)
  if (!context) {
    throw new Error('useCareerPreferences must be used within a CareerPreferenceProvider')
  }
  return context
}
