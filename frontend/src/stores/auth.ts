import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type UserInfo, type UserRole } from '@/api/services'

function loadStoredUser(): UserInfo | null {
  try {
    const raw = localStorage.getItem('user_info')
    return raw ? (JSON.parse(raw) as UserInfo) : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('access_token') || '')
  const user = ref<UserInfo | null>(loadStoredUser())

  const isAuthenticated = computed(() => Boolean(token.value && user.value))
  const role = computed<UserRole | null>(() => user.value?.role ?? null)

  function setSession(access: string, refresh: string, userInfo: UserInfo) {
    token.value = access
    user.value = userInfo
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    localStorage.setItem('user_info', JSON.stringify(userInfo))
  }

  function updateUser(userInfo: UserInfo) {
    user.value = userInfo
    localStorage.setItem('user_info', JSON.stringify(userInfo))
  }

  async function refreshProfile() {
    if (!token.value) return
    const { data } = await authApi.getProfile()
    updateUser(data)
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  }

  return {
    token,
    user,
    role,
    isAuthenticated,
    setSession,
    updateUser,
    refreshProfile,
    logout
  }
})
