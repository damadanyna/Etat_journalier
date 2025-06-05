<template>
    <v-container fluid class=" h-full  ">
      <v-row no-gutters class="">
        <!-- Partie gauche : 65% -->
        <v-col   cols="12" sm="12" md="9"class="pa-4   overflow-auto max-h-[90vh]">
          <v-row>
            <v-col
              v-for="(product, index) in products"
              :key="index"
              cols="12" sm="6" md="4"
            >
              <v-card elevation="0" 
              class="border border-stone-400"  @click="selectProduct(product)">
              <v-img 
                aspect-ratio="16/9"
                cover
                src="https://cdn.vuetifyjs.com/images/parallax/material.jpg"
                ></v-img>
                <v-card-title>{{ product.name }}</v-card-title>
                <v-card-text>{{ product.description }}</v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-col>
  
        <!-- Partie droite : 35%, hauteur 100% -->
        <v-col
          :cols="3"
          class=" flex-column border hidden lg:flex border-stone-400 h-[91vh]"
        >
          <v-card elevation="0" class="pa-4  bg-transparent">
            <v-card-title>Propriétés</v-card-title>
            <v-card-text v-if="selectedProduct">
              <p><strong>Nom :</strong> {{ selectedProduct.name }}</p>
              <p><strong>Description :</strong> {{ selectedProduct.description }}</p>
            </v-card-text>
            <v-card-text v-else>
              <em>Sélectionnez un produit pour voir les détails</em>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </template>
  
  
  <script setup>
  import { ref } from 'vue'
  
  const products = [
    { name: 'Produit A', description: 'Description A' },
    { name: 'Produit B', description: 'Description B' },
    { name: 'Produit C', description: 'Description C' },
    { name: 'Produit D', description: 'Description D' },
    { name: 'Produit E', description: 'Description E' },
    { name: 'Produit F', description: 'Description F' }
  ]
  
  const selectedProduct = ref(null)
  
  function selectProduct(product) {
    selectedProduct.value = product
  }
  </script>

  <style scoped>
  .v-container {
    height: 100vh;
    padding: 0px;
  }
  </style>
  