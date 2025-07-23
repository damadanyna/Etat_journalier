<template>
  <v-tabs v-model="tab" >
      <v-tab value="one">Création</v-tab>
      <v-tab value="two">Listes</v-tab>
    </v-tabs>
    <v-tabs-window v-model="tab" style="margin-top: 50px; background-color: #212121; padding: 5px 40px; border-radius: 10px;">
      <v-tabs-window-item value="one" style=" ">
        <v-card title="Liste des Déclarations" flat>
          <!-- <template v-slot:text>
            <v-text-field v-model="" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
          </template>
          <v-data-table :headers="headers" :items="list_encours" @click:row="onRowClick"  v-model="selectedItems"  item-value="Numero_pret" :search="search" fixed-header height="400px" item-key="id"  >
             
            <template v-slot:item.ID="{ item }">
              {{ item.ID ? item.ID.slice(0, 2) : '' }}
            </template>

            <template #item.index="{ index }">
              {{ index + 1 }}
            </template>
          </v-data-table> -->
        </v-card>
      </v-tabs-window-item>

      
      <v-tabs-window-item value="two">
        <button class="customize_btn" @click="onRowClick_atraiter_">
          <v-icon icon="mdi mdi-download-circle" size="24" />
          Génerer le '.txt'
        </button>
        <v-card title="Liste des déclarations faites" flat>
          <template v-slot:text>
            <v-text-field v-model="search" label="Search" prepend-inner-icon="mdi-magnify" variant="outlined" hide-details single-line></v-text-field>
          </template>
          <!-- <v-data-table :headers="headers_a_traiter" :items="list_a_traiter_"   v-model="selectedItems_a_traiter"  item-value="Numero_pret" :search="search_a_traiter" fixed-header height="400px" item-key="id"  ></v-data-table> -->
        </v-card>
      </v-tabs-window-item>
    </v-tabs-window>
</template>

<script setup>
import { ref } from 'vue';

const search=ref('')
 
</script>

<style>

</style>