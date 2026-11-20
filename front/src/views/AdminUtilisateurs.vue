<template>
  <main class="form-panel">
    <h1>Utilisateurs enregistrés</h1>
    <p v-if="!users.length">Aucun utilisateur enregistré.</p>

    <table v-else class="accounts-table">
      <thead>
        <tr>
          <th scope="col">Login</th>
          <th scope="col">Action</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <th scope="row">{{ user.login }}</th>
          <td>
            <button type="button" :aria-label="'Supprimer ' + user.login" @click="remove(user)">
              Supprimer
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { deleteUser, listUsers } from '@/services/authService.js'

const users = ref(listUsers())

function remove(user) {
  if (window.confirm(`Supprimer le compte ${user.login} ?`)) {
    deleteUser(user.id)
    users.value = listUsers()
  }
}
</script>