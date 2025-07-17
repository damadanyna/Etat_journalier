<template>
  <div class="w-full h-full flex items-center justify-center absolute top-0 left-0 backdrop-blur-sm">
    <v-sheet class="pa-4 text-center mx-auto" elevation="12" max-width="600" rounded="lg" width="100%">
      <span class="text-2xl">Importation</span>

      <v-divider class="mb-4" ></v-divider>  
        <div v-if="popupStore.loadFile!='Fait'" >
            {{ popupStore.loadFile }}
        </div>
        <div v-else> 
            <v-icon
            class="mb-5"
            color="success"
            icon="mdi-check-circle"
            size="112"
            ></v-icon> 
            <h2 class=" mb-6">Toutes les fichies sont importées</h2>
        </div>
 
    </v-sheet>
  </div>
</template>

<script setup>
import { usePopupStore } from '../../stores'

const popupStore = usePopupStore()
</script>
