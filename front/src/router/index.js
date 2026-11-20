import { createRouter, createWebHistory } from 'vue-router'
import Accueil from '@/views/Accueil.vue'
import Authentification from '@/views/Authentification.vue'
import AdminUtilisateurs from '@/views/AdminUtilisateurs.vue'
import AdminAccueil from '@/views/AdminAccueil.vue'
import { useAuthStore } from '@/stores/auth.js'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'accueil', component: Accueil },
    { path: '/login', name: 'login', component: Authentification },
    { path: '/admin/utilisateurs', component: AdminUtilisateurs, meta: { admin: true } },
    { path: '/admin/accueil', component: AdminAccueil, meta: { admin: true } },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.admin && !auth.session) return { name: 'login' }
  if (to.meta.admin && auth.session.user.role !== 'admin') return { name: 'accueil' }
})

export default router