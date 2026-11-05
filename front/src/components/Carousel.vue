<template>
  <div class="carousel">
    <button class="nav-btn prev" @click="prev">‹</button>
    
    <div class="carousel-slide" v-if="items.length > 0">
      <img :src="items[currentIndex].src" :alt="items[currentIndex].alt" />
      <p class="legend">{{ items[currentIndex].title }}</p>
    </div>

    <button class="nav-btn next" @click="next">›</button>

    <div class="dots">
      <span 
        v-for="(item, index) in items" 
        :key="item.id" 
        :class="{ active: index === currentIndex }"
        @click="currentIndex = index"
      ></span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true
  }
})

const currentIndex = ref(0)

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % props.items.length
}

const prev = () => {
  currentIndex.value = (currentIndex.value - 1 + props.items.length) % props.items.length
}
</script>

<style scoped>
.carousel {
  position: relative;
  max-width: 580px;
  margin: 1.5rem auto;
}

.carousel-slide {
  background-color: #ffffff;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.carousel-slide img {
  width: 100%;
  height: auto;
  display: block;
}

.legend {
  margin-top: 0.5rem;
  font-weight: 600;
  font-size: 0.95rem;
  color: #1e293b;
}

.nav-btn {
  position: absolute;
  top: 45%;
  transform: translateY(-50%);
  background: #1e293b;
  color: white;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.prev { left: -18px; }
.next { right: -18px; }

.dots {
  display: flex;
  justify-content: center;
  gap: 0.4rem;
  margin-top: 1rem;
}

.dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  cursor: pointer;
}

.dots span.active {
  background: #1e293b;
  width: 18px;
  border-radius: 4px;
}
</style>