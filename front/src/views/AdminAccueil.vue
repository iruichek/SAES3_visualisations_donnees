<template>
  <main class="form-panel">
    <h1>Modifier l’accueil</h1>

    <form @submit.prevent="save">
      <label>
        Texte de présentation
        <textarea v-model="description" rows="6" required />
      </label>

      <label v-for="(item, index) in carouselItems" :key="item.id">
        URL du graphique {{ index + 1 }}
        <input v-model.trim="urls[index]" required />
      </label>

      <p v-if="error" role="alert">{{ error }}</p>
      <p v-if="message" role="status">{{ message }}</p>
      <button>Enregistrer</button>
    </form>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { getHomeContent, saveHomeContent } from '@/services/homeContentService.js'

const content = getHomeContent()
const carouselItems = content.carouselItems
const description = ref(content.description)
const urls = ref(carouselItems.map((item) => item.src))
const message = ref('')
const error = ref('')

function save() {
  error.value = ''
  message.value = ''

  try {
    saveHomeContent(description.value, urls.value)
    message.value = 'Modifications enregistrées.'
  } catch (cause) {
    error.value = cause.message
  }
}
</script>