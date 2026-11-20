import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login } from '@/services/authService.js'

const sessionKey = 'nuage-sur-les-rails:session'

function restoreSession() {
  try {
    const saved = JSON.parse(localStorage.getItem(sessionKey) ?? 'null')
    return saved?.user?.login && saved.sessionId ? saved : null
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const session = ref(restoreSession())

  async function signIn(credentials) {
    const result = await login(credentials)
    localStorage.setItem(sessionKey, JSON.stringify(result))
    session.value = result
  }

  function signOut() {
    localStorage.removeItem(sessionKey)
    session.value = null
  }

  return { session, signIn, signOut }
})