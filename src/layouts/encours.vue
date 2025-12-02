<template>
  <v-app >
    <NavigationDrawer ref="drawer"/> 
    <v-main class=" h-full  flex-column">
      <menu_bar></menu_bar>
      <slot />
    </v-main>
  </v-app>
</template>

<script setup>
import NavigationDrawer from '@/components/navigation_drawer.vue'  
import menu_bar from '../components/menu_bar.vue';
import { ref } from 'vue'
const drawer = ref(null)
</script>

<style scoped>
 
</style>

  