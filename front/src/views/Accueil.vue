<template>
  <main>
    <header>
      <h1>NuageSurLesRails</h1>
    </header>

    <section>
      <h2>
        NuageSurLesRails est une plateforme web destinée à explorer et analyser les impacts des conditions météorologiques sur la ponctualité des TER en France.
        Le site croise les données de régularité du réseau ferroviaire avec les relevés climatiques régionaux pour visualiser l'influence du temps sur le trafic.
      </h2>
    </section>

    <footer>
    </footer>
  </main>
</template>

<style scoped>
main {
  min-height: calc(100vh - 70px);
  /* Fond bleu ciel uni sur toute la page comme le site de référence */
  background-color: #cbe8ff;
  color: #1a202c;
  font-family: system-ui, -apple-system, sans-serif;
  display: flex;
  flex-direction: column;
  align-items: center;
}

header {
  width: 100%;
  padding: 3.5rem 1rem 1rem 1rem;
  text-align: center;
  /* Fond transparent pour conserver le fond bleu de <main> */
  background: transparent;
}

h1 {
  margin: 0;
  font-size: 3.2rem;
  font-weight: 800;
  color: #1e293b;
  letter-spacing: -1px;
}

section {
  max-width: 750px;
  margin: 1rem auto;
  padding: 0 1.5rem;
  text-align: center;
}

h2 {
  font-size: 1.25rem;
  font-weight: 500;
  line-height: 1.6;
  color: #1e293b;
}

footer {
  margin-top: auto;
  padding: 2rem;
  width: 100%;
}

@media (max-width: 768px) {
  h1 {
    font-size: 2.25rem;
  }
  
  h2 {
    font-size: 1.05rem;
  }
}
</style>