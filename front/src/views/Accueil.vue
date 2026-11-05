<template>
  <main>
    <!-- La grande bande centrale qui regroupe tout le contenu -->
    <div class="content-container">
      <header>
        <h1>NuageSurLesRails</h1>
      </header>

      <section class="description-section">
        <h2>
          NuageSurLesRails est une plateforme web destinée à explorer et analyser les impacts des conditions météorologiques sur la ponctualité des TER en France.
          Le site croise les données de régularité du réseau ferroviaire avec les relevés climatiques régionaux pour visualiser l'influence du temps sur le trafic.
        </h2>
      </section>

      <section class="carousel-section">
        <Carousel :items="carouselItems" />
      </section>

      <section class="cta-section">
        <div class="cta-card">
          <p class="cta-text">
            <strong>Envie d'aller plus loin ?</strong>
            Connectez-vous pour accéder aux outils d'analyse descriptive
            et aux statistiques par région.
          </p>
          <RouterLink to="/login" class="cta-button">
            Se connecter
          </RouterLink>
        </div>
      </section>
    </div>

    <footer>
    </footer>
  </main>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Carousel from '@/components/Carousel.vue'
import { getCarouselItems } from '@/services/carouselService.js'

const carouselItems = ref([])

onMounted(() => {
  carouselItems.value = getCarouselItems()
})
</script>

<style scoped>
main {
  min-height: calc(100vh - 70px);
  /* Le fond de la page reste bleu ciel */
  background-color: #cbe8ff;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem 1rem;
  font-family: system-ui, -apple-system, sans-serif;
}

/* La bande / carte blanche au centre */
.content-container {
  background-color: #ffffff;
  width: 100%;
  max-width: 850px; /* Largeur maximale de la bande centrale */
  padding: 3rem 2.5rem;
  border-radius: 16px; /* Coins arrondis élégants */
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06); /* Ombre douce */
}

header {
  text-align: center;
  margin-bottom: 1.5rem;
}

h1 {
  margin: 0;
  font-size: 3rem;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: -1px;
}

.description-section {
  text-align: center;
  margin-bottom: 2rem;
}

h2 {
  font-size: 1.15rem;
  font-weight: 400;
  line-height: 1.6;
  color: #475569;
}

.carousel-section {
  margin-bottom: 2rem;
}

/* La carte CTA dans la bande centrale */
.cta-card {
  background-color: #f8fafc; /* Gris très léger pour contraster avec la bande blanche */
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
}

.cta-text {
  margin: 0 0 1rem 0;
  color: #1e293b;
  font-weight: 500;
}

.cta-button {
  display: inline-block;
  background-color: #1e293b;
  color: #ffffff;
  padding: 0.75rem 1.75rem;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: background-color 0.2s ease;
}

.cta-button:hover {
  background-color: #0284c7;
}

@media (max-width: 768px) {
  .content-container {
    padding: 1.5rem 1rem;
    border-radius: 12px;
  }

  h1 {
    font-size: 2.2rem;
  }
}
</style>