<template>
  <VApp class="h-screen" >
      <LayoutDefault>
      <router-view />
    </LayoutDefault>
    <VSnackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
    >
      {{snackbar.text}}
      <template #actions>
        <VBtn color="white" variant="text" @click="snackbar.show = false">
          Close
        </VBtn>
      </template>
    </VSnackbar>
  </VApp>
</template>

<script setup>

import LayoutDefault from '@/layouts/default.vue'
import { useSnackbar } from '@/composables/useSnackbar' 
import { useTheme } from 'vuetify' 
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { onMounted } from 'vue'

const { snackbar } = useSnackbar()
const { global } = useTheme() 
  
const route = useRoute()

const layout = computed(() => route.meta.layout || 'default')

onMounted(() => { 
  const theme = localStorage.getItem('theme')
  if (theme) {
    global.name.value = theme
  }
   
})

// Optionally, handle dynamic layouts here if necessary
</script>
<style>
/* Cache la scrollbar sur tous les navigateurs */
html, body {
  overflow: hidden;
}

/* Facultatif : si tu veux quand même que le contenu puisse scroller via la molette sans scrollbar visible */
body {
  scrollbar-width: none; /* Firefox */
}

body::-webkit-scrollbar {
  display: none; /* Chrome, Safari */
}
#app{
  overflow: hidden;
}
</style>  