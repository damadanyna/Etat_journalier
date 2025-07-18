<template>
        <v-navigation-drawer
          v-model="drawer"
          :rail="rail"
          permanent 
        >
          <v-list-item 
            title="Dama Dany"
            nav
            
            @click.stop="rail = !rail"
          > 
            <template v-slot:append>
              <v-btn
                icon="mdi-menu"
                variant="text"
              ></v-btn>
            </template>
          </v-list-item>
  
          <v-divider></v-divider>
  
          <v-list density="compact" nav>
            <v-list-item
            v-for="item in list_menu" :key="item"
              :to="item.to"
              :prepend-icon="item.icon"
              :title="item.title"
              color="green-accent-3"
            ></v-list-item> 
         
          </v-list>
        </v-navigation-drawer> 
  </template>

<script setup> 
import { ref } from 'vue';
const drawer = ref(true);
const rail = ref(true);

const list_menu = [
  { icon: 'mdi-home-city', title: 'Crédits', to: '/app/credits' },
  { icon: 'mdi-account', title: 'My Account', to: '/app/another' },
  { icon: 'mdi-file-table-box-multiple-outline', title: 'Mes Fichier', to: '/app/file_manager' },
  { icon: 'mdi-map-marker-radius', title: 'Users', to: '/app/getMyloc' },
]
 
</script>