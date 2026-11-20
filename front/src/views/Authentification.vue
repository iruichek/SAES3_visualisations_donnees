<template>
  <main class="form-panel">
    <h1>{{ inscription ? 'Créer un compte' : 'Se connecter' }}</h1>

    <form @submit.prevent="submit">
      <label>
        Login
        <input v-model.trim="identifiant" autocomplete="username" required />
      </label>

      <label>
        Mot de passe
        <input
          v-model="password"
          type="password"
          :autocomplete="inscription ? 'new-password' : 'current-password'"
          required
        />
      </label>

      <p v-if="error" role="alert">{{ error }}</p>
      <p v-if="message" role="status">{{ message }}</p>

      <button :disabled="busy">{{ inscription ? 'S’inscrire' : 'Se connecter' }}</button>
    </form>

    <button type="button" class="secondary" :disabled="busy" @click="changeMode">
      {{ inscription ? 'J’ai déjà un compte' : 'Créer un compte' }}
    </button>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { register } from '@/services/authService.js'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()
const router = useRouter()
const identifiant = ref('')
const password = ref('')
const inscription = ref(false)
const busy = ref(false)
const error = ref('')
const message = ref('')

function changeMode() {
  inscription.value = !inscription.value
  password.value = ''
  error.value = ''
  message.value = ''
}

async function submit() {
  busy.value = true
  error.value = ''
  message.value = ''

  try {
    const credentials = { login: identifiant.value, password: password.value }

    if (inscription.value) {
      await register(credentials)
      changeMode()
      message.value = 'Compte créé. Tu peux maintenant te connecter.'
      return
    }

    await auth.signIn(credentials)
    await router.push({ name: 'accueil' })
  } catch (cause) {
    error.value = cause.message
  } finally {
    busy.value = false
  }
}
</script>