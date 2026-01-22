import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import type { User, UserProfile } from '@/lib/types'

export function useUserProfile(userId: string) {
  const [user, setUser] = useState<User | null>(null)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!userId) return

    const fetchUser = async () => {
      try {
        setLoading(true)
        const userData = await api.getUser(userId)
        setUser(userData)
        setProfile(userData.profile || null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch user')
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [userId])

  const updateProfile = async (newProfile: Partial<UserProfile>) => {
    try {
      setLoading(true)
      const updatedProfile = { ...profile, ...newProfile }
      await api.updateProfile(userId, updatedProfile)
      setProfile(updatedProfile)
      return true
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile')
      return false
    } finally {
      setLoading(false)
    }
  }

  return {
    user,
    profile,
    loading,
    error,
    updateProfile,
  }
}
