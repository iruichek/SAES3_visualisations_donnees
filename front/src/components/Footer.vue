<template>
  <footer class="site-footer">
    <p>Références des API</p>

    <ul class="footer-links">
      <li>
        <a href="https://data.sncf.com/explore/dataset/regularite-mensuelle-ter/table/?sort=date">
          SNCF Open Data — Régularité mensuelle des TER
        </a>
      </li>
      <li>
        <a href="https://open-meteo.com/en/docs/meteofrance-api">
          Open-Meteo — API Météo-France
        </a>
      </li>
    </ul>
  </footer>
</template>

<style scoped>
.site-footer {
  padding: 3rem 1.5rem;
  background-color: #1e293b;
  color: #f8fafc;
  font-family: system-ui, sans-serif;
  text-align: center;
}

.site-footer p {
  margin: 0 0 1.25rem;
  font-weight: 600;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.75rem 2.5rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.footer-links a {
  color: #cbe8ff;
}
</style>