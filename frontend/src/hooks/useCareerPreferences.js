import { useCareerPreferences } from '../context/CareerPreferenceContext'

export const useCareerPreferencesHook = () => {
  const { preferences, updatePreferences, loading, saveSuccess, refreshPreferences } = useCareerPreferences()
  return {
    preferences,
    updatePreferences,
    loading,
    saveSuccess,
    refreshPreferences
  }
}

export default useCareerPreferencesHook
