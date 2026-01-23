// API client for communicating with FastAPI backend

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface FetchOptions extends RequestInit {
  userId?: string
}

async function fetchAPI(endpoint: string, options: FetchOptions = {}) {
  const { userId, ...fetchOptions } = options

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  // Add any existing headers
  if (fetchOptions.headers) {
    Object.assign(headers, fetchOptions.headers)
  }

  if (userId) {
    headers['X-User-Id'] = userId
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...fetchOptions,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export const api = {
  // Users - Fixed endpoints to match backend
  async createUser(data: { id: string; username: string }) {
    return fetchAPI('/users/', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  async getMe(userId: string) {
    return fetchAPI('/users/me', { userId })
  },

  async updateProfile(userId: string, profile: any) {
    return fetchAPI('/users/me/profile', {
      method: 'PUT',
      userId,
      body: JSON.stringify(profile),
    })
  },

  // Workout Plans - Fixed endpoints
  async generateWorkoutPlan(userId: string) {
    return fetchAPI('/plans/workout', {
      method: 'POST',
      userId,
    })
  },

  async getCurrentWorkoutPlan(userId: string) {
    return fetchAPI('/plans/workout/current', {
      userId,
    })
  },

  async activateWorkoutPlan(planId: string, userId: string) {
    return fetchAPI(`/plans/workout/${planId}/activate`, {
      method: 'POST',
      userId,
    })
  },

  // Nutrition Plans - Fixed endpoints
  async generateNutritionPlan(userId: string) {
    return fetchAPI('/plans/nutrition', {
      method: 'POST',
      userId,
    })
  },

  async getCurrentNutritionPlan(userId: string) {
    return fetchAPI('/plans/nutrition/current', {
      userId,
    })
  },

  async activateNutritionPlan(planId: string, userId: string) {
    return fetchAPI(`/plans/nutrition/${planId}/activate`, {
      method: 'POST',
      userId,
    })
  },

  // Notifications
  async getNotifications(userId: string, unreadOnly: boolean = false) {
    const params = new URLSearchParams({ unread_only: unreadOnly.toString() })
    return fetchAPI(`/notifications?${params}`, {
      userId,
    })
  },

  async markNotificationAsRead(notificationId: string, userId: string) {
    return fetchAPI(`/notifications/${notificationId}/read`, {
      method: 'PATCH',
      userId,
    })
  },

  // Comments
  async getComments(planId: string, planType: 'workout' | 'nutrition', userId: string) {
    return fetchAPI(`/comments/${planType}/${planId}`, {
      userId,
    })
  },

  async addComment(planId: string, planType: 'workout' | 'nutrition', content: string, userId: string) {
    return fetchAPI(`/comments/${planType}/${planId}`, {
      method: 'POST',
      userId,
      body: JSON.stringify({ content }),
    })
  },

  // Versions
  async getPlanVersions(planId: string, planType: 'workout' | 'nutrition', userId: string) {
    return fetchAPI(`/versions/${planType}/${planId}`, {
      userId,
    })
  },
}

