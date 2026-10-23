<template>
  <nav aria-label="Navigation principale">
    <RouterLink to="/">Accueil</RouterLink>
  </nav>
</template>

<style scoped>
nav {
  padding: 1rem 2rem;
  background-color: #1e293b;
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

a {
  color: #ffffff;
  text-decoration: none;
  font-family: system-ui, -apple-system, sans-serif;
  font-size: 1rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  transition: opacity 0.2s ease;
}

a:hover {
  opacity: 0.8;
  text-decoration: none;
}

.router-link-active {
  font-weight: bold;
}
</style>