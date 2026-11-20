<template>
  <main class="home">
    <header class="hero">
      <div>
        <h1>Mauvaise météo et trains ne font pas bon ménage.</h1>
        <p>
          Visualisez l’impact des conditions météorologiques sur la ponctualité des TER en France.
        </p>
      </div>
    </header>


    <div class="row row--graphs">
      <Carousel :items="carouselItems" />

      <p>{{ description }}</p>
    </div>

    <div v-if="!auth.session" class="row row--login">
      <p>
        <strong>Envie d’aller plus loin ?</strong>
        Connectez-vous pour accéder aux outils d’analyse descriptive et aux statistiques par région.
      </p>

      <RouterLink to="/login" class="login-link">Se connecter</RouterLink>
    </div>
  </main>
</template>

<script setup>
import Carousel from '@/components/Carousel.vue'
import { getHomeContent } from '@/services/homeContentService.js'
import { useAuthStore } from '@/stores/auth.js'

const auth = useAuthStore()
const { description, carouselItems } = getHomeContent()
</script>

<style scoped>
.home {
  font-family: system-ui, sans-serif;
  color: #1e293b;
}

.hero {
  display: grid;
  place-items: center;
  box-sizing: border-box;
  min-height: 90svh;
  padding: 2rem 1.5rem;
  background: linear-gradient(#0f172a99, #0f172abf),
    #1e293b url('../public/images/Train.jpeg') center / cover no-repeat;
  color: white;
  text-align: center;
}

.hero h1 {
  max-width: 50ch;
  margin: 0 auto 1rem;
  font-size: clamp(2rem, 5vw, 3rem);
  line-height: 1.1;
  text-wrap: balance;
}

.hero p {
  max-width: 55ch;
  margin: 0 auto;
  font-size: clamp(1rem, 2vw, 1.35rem);
  line-height: 1.5;
}

.row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: center;
  gap: 2rem;
  padding: 3rem max(2rem, calc((100% - 1100px) / 2));
}

.row--graphs {
  column-gap: clamp(3rem, 6vw, 5rem);
  background-color: #fff;
}

.row--login {
  background-color: #e6f3ff;
}

@media (max-width: 700px) {
  .row {
    grid-template-columns: 1fr;
    gap: 1rem;
    padding-block: 2rem;
  }

  .row--graphs {
    row-gap: 1.5rem;
  }
}

.row p {
  margin: 0;
  font-size: 1.125rem;
  line-height: 1.65;
}

.login-link {
  justify-self: center;
  padding: 0.8rem 1.5rem;
  border-radius: 0.5rem;
  background-color: #1e293b;
  color: #fff;
  font-weight: 600;
  text-decoration: none;
}

.login-link:hover {
  background-color: #334155;
}
</style>