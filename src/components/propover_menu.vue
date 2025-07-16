<template> 
  
      <v-main  >
        <div :class="drawer==true?'opacity-0':'right-3 opacity-100'" class=" duration-200 absolute z-[50] top-1/2">
          <v-icon icon="mdi mdi-cog" size="24"   @click="drawer = !drawer"></v-icon>
        </div>
      </v-main>
      <v-navigation-drawer v-model="drawer" temporary location="right"  elevation="5" >
        <v-card class=" px-2"  >
            <span>Theme</span>
            <div class="flex px-5 w-full justify-between">
                <v-icon icon="mdi mdi-weather-sunny" size="24" 
                @click="setLightTheme"></v-icon>
                <v-icon icon="mdi mdi-weather-night" size="24"
                @click="setDarkTheme"></v-icon>
            </div>
        </v-card>
  
        <v-divider></v-divider>
  
        <v-list density="compact" nav>
          <v-list-item prepend-icon="mdi-view-dashboard" title="Home" value="home"></v-list-item>
          <v-list-item prepend-icon="mdi-forum" title="About" value="about"></v-list-item>
        </v-list>
      </v-navigation-drawer> 

  </template>
  
  <script setup>
import { ref } from 'vue';
import { useTheme } from 'vuetify'
const { global } = useTheme()
const drawer= ref(false)
 
  
// Définit le thème en clair
const setLightTheme=()=> {
  global.name.value = 'light'
  localStorage.setItem('theme', 'light')
}

// Définit le thème en sombre
const setDarkTheme=()=> {
  global.name.value = 'dark'
  localStorage.setItem('theme', 'dark')
} 
  </script>
  