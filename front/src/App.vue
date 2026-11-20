<template>
  <NavBar />
  <RouterView />
  <SiteFooter />
</template>

<script setup>
import NavBar from './components/NavBar.vue'
import SiteFooter from './components/Footer.vue'
</script>

<style>
body {
  margin: 0;
}
.form-panel {
  box-sizing: border-box;
  width: min(36rem, calc(100% - 2rem));
  margin: 3rem auto;
  padding: clamp(1rem, 4vw, 2rem);
  border-radius: 0.75rem;
  background: #f1f5f9;
  color: #1e293b;
  font-family: system-ui, sans-serif;
}

.form-panel h1 { margin-top: 0; }
.form-panel form,
.form-panel label { display: grid; gap: 0.5rem; }
.form-panel form { gap: 1rem; }

.form-panel input,
.form-panel textarea {
  box-sizing: border-box;
  width: 100%;
  padding: 0.65rem;
  border: 1px solid #94a3b8;
  border-radius: 0.4rem;
  font: inherit;
}

.form-panel button {
  justify-self: start;
  padding: 0.65rem 1rem;
  border: 0;
  border-radius: 0.4rem;
  background: #1e293b;
  color: white;
  font: inherit;
  cursor: pointer;
}

.form-panel .secondary {
  margin-top: 0.75rem;
  padding-inline: 0;
  background: transparent;
  color: #1e293b;
  text-decoration: underline;
}

.form-panel [role="alert"] { color: #991b1b; }
.accounts-table {
  width: 100%;
  border-collapse: collapse;
}

.accounts-table th,
.accounts-table td {
  padding: 0.75rem 0.5rem;
  border-bottom: 1px solid #cbd5e1;
  text-align: left;
  overflow-wrap: anywhere;
}

.accounts-table thead {
  background: #e2e8f0;
}

.accounts-table tr > :last-child {
  text-align: right;
}
</style>