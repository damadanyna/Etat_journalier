<template>
  <v-app >
    <NavigationDrawer />
    <!-- <Propover_menu  /> -->
    <v-main class=" h-full  flex-column">
      <menu_bar></menu_bar>
      <slot />
    </v-main>
  </v-app>
</template>

<script setup>
import NavigationDrawer from '@/components/navigation_drawer.vue' // ou '../components/' selon ton arborescence
// import Propover_menu from '@/components/propover_menu.vue';
import menu_bar from '../components/menu_bar.vue';
</script>

<style scoped>
 
</style>

