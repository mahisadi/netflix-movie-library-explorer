import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUserStore = defineStore('user', () => {
  // State
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Actions
  const fetchRandomUser = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await fetch('https://randomuser.me/api/')
      const data = await response.json()
      
      if (data.results && data.results.length > 0) {
        user.value = data.results[0]
      } else {
        throw new Error('No user data received')
      }
    } catch (err) {
      error.value = err.message
      console.error('Error fetching random user:', err)
    } finally {
      loading.value = false
    }
  }

  const clearUser = () => {
    user.value = null
    error.value = null
  }

  // Getters
  const getUserFullName = () => {
    if (!user.value) return ''
    return `${user.value.name.first} ${user.value.name.last}`
  }

  const getUserInitials = () => {
    if (!user.value) return 'U'
    return `${user.value.name.first[0]}${user.value.name.last[0]}`.toUpperCase()
  }

  const getUserLocation = () => {
    if (!user.value) return ''
    return `${user.value.location.city}, ${user.value.location.country}`
  }

  return {
    // State
    user,
    loading,
    error,
    // Actions
    fetchRandomUser,
    clearUser,
    // Getters
    getUserFullName,
    getUserInitials,
    getUserLocation
  }
})
