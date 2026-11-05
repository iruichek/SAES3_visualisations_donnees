<template>
  <header class="navbar">
    <div class="nav-container">
      
      <!-- Logo avec la couleur du fond de la page d'accueil -->
      <RouterLink to="/" class="brand">
        <span class="brand-text">NuageSurLesRails</span>
      </RouterLink>

      <!-- Navigation principale -->
      <nav aria-label="Navigation principale">
        <RouterLink to="/" class="nav-link">Accueil</RouterLink>
        
        <!-- Lien de connexion -->
        <RouterLink to="/login" class="login-button">
          Se connecter
        </RouterLink>
      </nav>

    </div>
  </header>
</template>

<style scoped>
.navbar {
  background-color: #1e293b;
  padding: 0.8rem 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.nav-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  text-decoration: none;
}

/* Texte du logo avec la même couleur que le fond d'accueil (#cbe8ff) */
.brand-text {
  font-size: 1.3rem;
  font-weight: 800;
  color: #cbe8ff;
  letter-spacing: -0.5px;
}

nav {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: #ffffff;
  text-decoration: none;
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 1rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  transition: opacity 0.2s ease;
}

.nav-link:hover {
  opacity: 0.8;
}

.router-link-active.nav-link {
  font-weight: bold;
}

/* Style du bouton "Se connecter" */
.login-button {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 0.45rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  font-size: 0.95rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.login-button:hover {
  background-color: #0284c7;
  border-color: #0284c7;
}
</style>