<template>
  <div id="app">
    <nmle-header />
    <main class="main-content">
      <router-view />
    </main>
    <nmle-footer />
  </div>
</template>

<script setup>
import NmleHeader from './components/NmleHeader.vue'
import NmleFooter from './components/NmleFooter.vue'
</script>

<style scoped>
.main-content {
  flex: 1;
  padding: 20px 0;
}
</style>
